# How to run EpiNano

0. First run the `create_virtual_env.sh` bash script within your working directory. This creates 2 virtual environments that are used by the EpiNano scripts. This only needs to ever be run once - unless you delete them.

## Prerequisites:
1. Basecalled reads are required. Ensure they are combined into one file with running this for example inside your basecalled reads folder `cat * > output.fastq.gz`. Path to this directory is required later on.

2. Get latest EpiNano code at `git clone https://github.com/enovoa/EpiNano.git` (writing this on 24/11/2020). Path to this directory is required later on.

3. Get human genome reference file. Path to this directory is required later on. e.g. UCSC Homo sapiens hg38 (.fa) from
 https://sapac.support.illumina.com/sequencing/sequencing_software/igenome.html

## Running EpiNano:
There are 4 main steps to get m6a modifications. Each step needs to be 100% completed (with no outstanding jobs) to move onto the next.

Please edit each step.pbs file (highlighted with "edit me") to have your own:
```
# Working directory (where output directory will be created).
my_dir="/srv/scratch/zid"
# Name of output folder and file prefixes.
output="INSERT_FOLDER_NAME_HERE"
# Path to the EpiNano directory
epinano_dir="$my_dir/EpiNano"
# Reference genome path:
genome_path="$my_dir/Homo_sapiens/UCSC/hg38/Sequence/WholeGenomeFasta/genome.fa"
# Basecall reads fastq path:
basecall_path="$my_dir/dir/pass/tissue.fastq.gz"
```

1. Submit job `qsub Running_Epinano/step1_align.pbs` which will map and index the basecalled reads.
2. Submit job `qsub Running_Epinano/step2_errorFeatureTable.pbs` which will create multiple jobs that generate an error feature table for epinano (this is the longest step).
3. Submit job `qsub Running_Epinano/step3_5mer.pbs` which converts the files to 5mers.
4. Submit job `qsub Running_Epinano/step4_predict.pbs` which creates the predictions.
5. Optionally submit job `qsub Running_Epinano/step5_summarise.pbs` which gives summary stats on the modifications found within a stats.txt file.

## Convert to bed
Optionally convert the csv output to BED format for analysis, with `python3 Running_Epinano/convert_csv_to_bed.py <input.csv> <output.bed>`

e.g.
```
python3 Running_Epinano/convert_csv_to_bed.py path/output/output_prediction_GGAC_CT_prediction_MODIFIED.csv path/output/output_prediction_GGAC_CT_prediction_MODIFIED.bed
python3 Running_Epinanos/convert_csv_to_bed.py path/output/output_prediction_GGAC_CT_prediction_UNMODIFIED.csv path/output/output_prediction_GGAC_CT_prediction_UNMODIFIED.bed
python3 Running_Epinano/convert_csv_to_bed.py path/output/output_prediction_GGAC_CT_cov_greater30.csv  path/output/output_prediction_GGAC_CT_cov_all.bed
```

## Analysis

###Gencode Example (get list of genes)
```
bedtools intersect -s -a brain_full/brain_prediction_GGAC[CT]_cov_greater30_UNMODIFIED.bed -b gencode.v35.annotation.gtf -wa -wb | awk '{if($9=="gene"){print $0}}' > brain_full/output_genes_only_UNMODIFIED.bed
python3 $my_dir/epinano_scripts/intersect_to_genes.py brain_full/output_genes_only_UNMODIFIED.bed brain_full/brain_UNMODIFIED_genes.txt

# Optional: get biotype summary
awk '{print $8}' brain_full/brain_modified_genes.txt | sort | uniq -c
```

###Annotatr
Use R script Annotatr to class your modifications as 3'UTR, 5'UTR or exon.

