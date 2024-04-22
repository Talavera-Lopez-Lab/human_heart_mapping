import pandas as pd
import os
import csv
import subprocess
import shutil

class Multiome_ATAC_Experiment():

    def __init__(
        self,
        rna_meta_path,
        atac_meta_path,
        meta_data_index,
        sample_col,
        file_name_col,
        url_col,
        parent_dir,
        cellranger_dir,
        cellranger_reference,
        mapping_output,
        keys=['rna', 'atac'],
    ):
        super().__init__()
        self.parent_dir = parent_dir
        self.data_dir = os.path.join(parent_dir, '.data')
        self.rna_meta_path = os.path.join(self.data_dir, rna_meta_path)
        self.atac_meta_path = os.path.join(self.data_dir, atac_meta_path)
        self.meta_data_index = meta_data_index
        self.sample_col = sample_col
        self.file_name_col = file_name_col
        self.url_col = url_col
        self.keys = keys
        self.pwd = os.getcwd()
        self.cellranger_dir = cellranger_dir
        self.cellranger_reference = os.path.join(self.data_dir, cellranger_reference)
        self.mapping_output = os.path.join(self.data_dir, mapping_output)
        self.meta_data = self.create_meta_data()
        self.runs = self.meta_data.index.unique()

    def create_meta_data(self):

        return pd.concat(
            [
                pd.read_table(self.rna_meta_path, index_col=self.meta_data_index),
                pd.read_table(self.atac_meta_path, index_col=self.meta_data_index),
            ],
            axis=1,
            keys=self.keys
        )

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
                '--localcores=20',
                '--localmem=32'
            ]
            subprocess.run(cellranger_arc_run)
            for key in self.keys:
                sample = download_df[key][self.sample_col][0]
                sample_dir = os.path.join(run_dir, sample)
                try:
                    shutil.rmtree(sample_dir)
                    print(f'{key} sample folder deleted')
                except OSError as e:
                    print(f"Error: {sample_dir} : {e.strerror}")