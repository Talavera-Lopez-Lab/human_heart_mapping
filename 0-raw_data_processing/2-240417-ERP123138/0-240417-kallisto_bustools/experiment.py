import pandas as pd
import os
import csv
import subprocess
import shutil
import glob

class TenX_GEX_Experiment():

    def __init__(
        self,
        parent_dir,
        meta_data_path,
        sample_col,
        file_name_col,
        url_col,
        mapping_output,
        mapped_samples=[],
        index_input_path='reference_data',
        index_output_path='index_output'
    ):
        super().__init__()
        self.parent_dir = parent_dir
        self.data_dir = os.path.join(parent_dir, '.data')
        self.index_input_path = os.path.join(self.data_dir, index_input_path)
        self.index_output_path = os.path.join(self.data_dir, index_output_path)
        self.meta_data_path = os.path.join(self.data_dir, meta_data_path)
        self.sample_col = sample_col
        self.file_name_col = file_name_col
        self.url_col = url_col
        self.mapping_output = os.path.join(self.data_dir, mapping_output)
        self.mapped_samples = mapped_samples
        self.meta_data = pd.read_csv(self.meta_data_path, index_col=self.sample_col)
        self.runs = self.meta_data.index.unique()

    def create_kallisto_bustools_index(self):
        os.makedirs(self.index_output_path, exist_ok=True)
        kb_ref_run = [
            'kb',
            'ref',
            '-i', f'{self.index_output_path}/transcriptome.idx',
            '-g', f'{self.index_output_path}/transcripts_to_genes.txt',
            '-f1', f'{self.index_output_path}/cdna.fa',
            '-f2', f'{self.index_output_path}/intron.fa',
            '-c1', f'{self.index_output_path}/cdna_transcripts_to_capture.txt',
            '-c2', f'{self.index_output_path}/intron_transcripts_to_capture.txt',
            '--workflow', 'lamanno',
            '--overwrite',
            f'{self.index_input_path}/GRCh38.p14.genome.fa',
            f'{self.index_input_path}/gencode.v45.chr_patch_hapl_scaff.annotation.gtf',
            f'{self.index_input_path}/gencode.v45.long_noncoding_RNAs.gtf',
        ]
        subprocess.run(kb_ref_run)

    def create_kallisto_bustools_mapping(self, threads=4, memory=8):
        '''This method downloads a dataset sample wise, maps them using kallisto bustools 
        and deletes the downloaded raw data'''
        def download_from_ftp(url, filepath):
            '''Helper for downloading files from ftp servers using bash command "axel"'''
            download_sample = [
                'axel', '-n', '10', '--output', filepath, url
            ]
            subprocess.run(download_sample)
        def run_kallisto_mapping(sample_dir):
            '''Helper for running the mapping process'''
            input_files = glob.glob(f'{sample_dir}/*.fastq.gz')
            kb_count_run = [
                'kb', 'count',
                '-i', os.path.join(self.index_output_path, 'transcriptome.idx'),
                '-g', os.path.join(self.index_output_path, 'transcripts_to_genes.txt'),
                '-x', '10XV3',
                '--h5ad',
                '--workflow', 'lamanno',
                '--verbose',
                '-t', f'{threads}',
                '-m', f'{memory}',
                '-c1', os.path.join(self.index_output_path, 'cdna_transcripts_to_capture.txt'),
                '-c2', os.path.join(self.index_output_path, 'intron_transcripts_to_capture.txt'),
            ] + input_files + [
                '-o', f'{sample_dir}'
            ]
            subprocess.run(kb_count_run)

        for outer_sample in self.runs:
            download_df = self.meta_data.loc[outer_sample]
            sample_dir = os.path.join(self.mapping_output, outer_sample)
            for inner_sample, data in download_df.iterrows():
                os.makedirs(sample_dir, exist_ok=True)
                filepath = os.path.join(sample_dir, data[self.file_name_col])
                url = data[self.url_col]
                download_from_ftp(url, filepath)
            raw_files = glob.glob(f'{sample_dir}/*.fastq.gz')
            # running the kallisto mapping algorithm
            run_kallisto_mapping(sample_dir)
            # Deleting the downloaded Raw fastqs
            for file in raw_files:
                if os.path.exists(file):
                    os.remove(file)
            raw_files = []

