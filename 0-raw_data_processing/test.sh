#!/bin/bash

# Declare an associative array with run accessions as keys and sample names as values
declare -A samples
samples=(
  ["ERR11403589"]="HCAHeart9508627"
  ["ERR11403590"]="HCAHeart9508628"
  ["ERR11403591"]="HCAHeart9508629"
  ["ERR11403592"]="HCAHeart9845431"
  ["ERR11403593"]="HCAHeart9845432"
)

# Base URL
base_url="ftp://ftp.sra.ebi.ac.uk/vol1/run/ERR114"

# File suffixes
suffixes=("S1_L001_I2_001.fastq.gz" "S1_L001_I1_001.fastq.gz" "S1_L001_R1_001.fastq.gz" "S1_L001_R2_001.fastq.gz")

# Iterate over the associative array
for accession in "${!samples[@]}"; do
  sample=${samples[$accession]}
  
  # Create a directory for each sample
  mkdir -p $sample
  
  # Change to the sample directory
  cd $sample
  
  # Iterate over the suffixes and download files
  for suffix in "${suffixes[@]}"; do
    # Construct the file URL
    file_url="${base_url}/${accession}/${sample}_${suffix}"
    echo $file_url
    
    # Use axel to download the file with 40 connections
    #axel -n 10 --output="${sample}_${suffix}" "$file_url"
  done
  
  # Change back to the parent directory
  cd ..
done