import pandas as pd
import os
import csv
import subprocess
import shutil

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
        '''This method downloads a dataset sample wise, maps them and deletes the downloaded raw data'''
        def download_from_ftp(filepath, url):
            '''Helper for downloading files from ftp servers using bash command "axel"'''
            download_sample = [
                'axel', '-n', '10', '--output', filepath, url
            ]
            subprocess.run(download_sample)
        def run_kallisto_mapping(sample):
            '''Helper for running the mapping process'''
            kb_count_run = [
                'kb', 'count',
                '-i', f'{self.index_output_path}transcriptome.idx',
                '-g', f'{self.index_output_path}transcripts_to_genes.txt',
                '-x', '10XV3',
                '--h5ad',
                '--workflow', 'lamanno',
                '--verbose',
                '-t', f'{threads}',
                '-m', f'{memory}',
                '-c1', f'{self.index_output_path}cdna_transcripts_to_capture.txt',
                '-c2', f'{self.index_output_path}intron_transcripts_to_capture.txt',
                f'{os.path.join(self.mapping_output, sample)}*.fastq.gz',
                '-o', f'{os.path.join(self.mapping_output, sample)}'
            ]
            subprocess.run(kb_count_run)


        for sample in self.runs:
            download_df = self.meta_data.loc[sample]
        for sample, data in self.meta_data.iterrows():
            sample_dir = os.path.join(self.mapping_output, sample)
            os.makedirs(sample_dir, exist_ok=True)
            filepath = os.path.join(sample_dir, data[self.file_name_col])
            url = data[self.url_col]

    def mapping(self):

        def write_csv(csv_file, data, mode):
            with open(csv_file, mode=mode, newline='') as file:
                writer = csv.writer(file)
                writer.writerows(data)

        for run in self.runs:
            run_dir = os.path.join(self.mapping_output, run)
            os.makedirs(run_dir, exist_ok=True)
            download_df = self.meta_data[self.meta_data.index == run]
            libraries_colums = [['fastqs', 'sample', 'library_type']]
            libraries_filepath = os.path.join(run_dir, 'libraries.csv')
            write_csv(libraries_filepath, libraries_colums, mode='w')
            for key in self.keys:
                sample = download_df[key][self.sample_col][0]
                sample_dir = os.path.join(run_dir, sample)
                os.makedirs(sample_dir, exist_ok=True)
                libraries_values = [[sample_dir, 
                                     sample, 
                                     'Gene Expression' if key == self.keys[0] else 'Chromatin Accessibility' if key == self.keys[1] else None]]
                write_csv(libraries_filepath, libraries_values, mode='a')
                file_dict = {row[self.file_name_col]: row[self.url_col] for index, row in download_df[key].iterrows()}
                for file_name, url in file_dict.items():
                    file_path = os.path.join(sample_dir, file_name)
                    subprocess.run(['axel', '-n', '10', '--output', file_path, url],
                                check=True)

                # Running Cellranger
            cellranger_arc_run = [
                self.cellranger_dir,
                'count',
                '--id=' + run,
                '--reference=' + self.cellranger_reference,
                '--libraries=' + libraries_filepath,
                '--localcores=32',
                '--localmem=128'
            ]
            subprocess.run(cellranger_arc_run)

            for file in os.listdir(run):
                if file.endswith('.bam'):
                    bam_path = os.path.join(run, file)
                    os.remove(bam_path)

            for key in self.keys:
                sample = download_df[key][self.sample_col][0]
                sample_dir = os.path.join(run_dir, sample)
                try:
                    shutil.rmtree(sample_dir)
                    print(f'{key} sample folder deleted')
                except OSError as e:
                    print(f"Error: {sample_dir} : {e.strerror}")

            shutil.move(run, run_dir)