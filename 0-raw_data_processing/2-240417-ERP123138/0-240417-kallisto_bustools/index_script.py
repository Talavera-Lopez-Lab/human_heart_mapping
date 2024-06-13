import experiment
import os

GEX_Experiment = experiment.TenX_GEX_Experiment(
    parent_dir=os.getcwd(),
    meta_data_path='meta_data/downloads_table.csv',
    sample_col='sample_accession',
    file_name_col='filename',
    url_col='url',
    mapping_output='mapping_py'
)

GEX_Experiment.create_kallisto_bustools_index()