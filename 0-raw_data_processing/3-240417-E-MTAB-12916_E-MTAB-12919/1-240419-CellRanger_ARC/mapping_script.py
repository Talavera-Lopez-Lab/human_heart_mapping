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
mapped_samples = [
    'HCAHeart9845431_HCAHeart9917173',
    'HCAHeart9845432_HCAHeart9917174',
    'HCAHeart9508627_HCAHeart9508819',
    'HCAHeart9845434_HCAHeart9917176',
    'HCAHeart9845435_HCAHeart9917177',
    'HCAHeart9845433_HCAHeart9917175',
    'HCAHeart9508628_HCAHeart9508820',
    'HCAHeart9508629_HCAHeart9508821'
]

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
    mapped_samples=mapped_samples
)

multiome_experiment.mapping()