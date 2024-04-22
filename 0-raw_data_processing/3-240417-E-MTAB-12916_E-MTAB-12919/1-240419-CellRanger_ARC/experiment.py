import pandas as pd
import os


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
        pass


