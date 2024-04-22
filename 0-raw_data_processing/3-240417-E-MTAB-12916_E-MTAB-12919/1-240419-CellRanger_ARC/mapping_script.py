from experiment import Multiome_ATAC_Experiment


rna_meta_path = 'meta_data/E-MTAB-12916.sdrf.txt'
atac_meta_path = 'meta_data/E-MTAB-12919.sdrf.txt'
meta_data_index = 'Description'
sample_col = 'Source Name'
file_name_col = 'Scan Name'
url_col = 'Comment[FASTQ_URI]'
parent_dir = '/mnt/LaCIE/ceger/Projects/human_heart_mapping/human_heart_mapping/0-raw_data_processing/3-240417-E-MTAB-12916_E-MTAB-12919/'
cellranger_dir = '/home/ceger/CellRanger/cellranger-arc-2.0.2/cellranger-arc'
cellranger_reference = 'cr_arc_index/GRCh38'
mapping_output = 'mapping_py'

multiome_experiment = Multiome_ATAC_Experiment(
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
)


multiome_experiment.mapping()