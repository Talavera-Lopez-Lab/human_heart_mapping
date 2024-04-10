#!/bin/bash

# Function to perform batched processing
batched_processing() {
    local df="$1"
    local sample_column="$2"
    local url_column="$3"
    local file_name_column="$4"
    local batch_size="$5"

    # Get unique sample names
    samples=$(awk -v sample_col="$sample_column" '{print $sample_col}' "$df" | sort | uniq)

    # Calculate number of batches
    num_samples=$(echo "$samples" | wc -l)
    num_batches=$(( ($num_samples + $batch_size - 1) / $batch_size ))

    # Iterate over batches
    for (( batch_id=0; batch_id<$num_batches; batch_id++ )); do
        start_id=$(( $batch_id * $batch_size ))
        end_id=$(( ($batch_id + 1) * $batch_size ))
        batch_names=$(echo "$samples" | sed -n "$(( $start_id + 1 )),$(( $end_id ))p")

        # Iterate over sample names in the batch
        while IFS= read -r name; do
            sample="$name"
            filtered_df=$(awk -v sample_col="$sample_column" -v name="$name" '$sample_col == name' "$df")

            # Iterate over files for the current sample
            while IFS= read -r line; do
                file_name=$(echo "$line" | awk -v file_name_col="$file_name_column" '{print $file_name_col}')
                file_url=$(echo "$line" | awk -v url_col="$url_column" '{print $url_col}')
                #echo "$file_url"
            done <<< "$filtered_df"
        done <<< "$batch_names"
    done
}

# Example usage:
batched_processing "../../raw_data/E-MTAB-12916.sdrf.txt" "Source Name" "Comment[FASTQ_URI]" "Scan Name" "5"