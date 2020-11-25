#!/usr/bin/env Rscript

if (!requireNamespace("BiocManager", quietly = TRUE))
  install.packages("BiocManager")

BiocManager::install("annotatr")
BiocManager::install("org.Hs.eg.db")

library("org.Hs.eg.db")
library("annotatr")

annots = c(
  'hg38_basicgenes',
  'hg38_lncrna_gencode'
)

# Build the annotations (a single GRanges object)
annotations = build_annotations(genome = 'hg38', annotations = annots)

library(dplyr) 

file <- "brain_modifications.bed" # Change file name.

dm_regions = read_regions(con = file, genome = 'hg38', format = 'bed', rename_name = 'mods', rename_score = 'mProbn')

dm_annotated = annotate_regions(
  regions = dm_regions,
  annotations = annotations,
  minoverlap=5,
  ignore.strand = FALSE,
  quiet = FALSE)

#print(dm_annotated)

dm_annsum = summarize_annotations(
  annotated_regions = dm_annotated,
  quiet = TRUE)

#print(dm_annsum)

# Ensure modifications are not in multiple categories.
# UTRs are classed as UTRs if they overlap with exon.

df_dm_annotated = data.frame(dm_annotated)

five_utrs = subset(df_dm_annotated, annot.type == 'hg38_genes_5UTRs')
unique_five_utrs = five_utrs [!duplicated(five_utrs[c(1,2,3)]),]

three_utrs = subset(df_dm_annotated, annot.type == 'hg38_genes_3UTRs')
unique_three_utrs = three_utrs [!duplicated(three_utrs[c(1,2,3)]),]

exons = subset(df_dm_annotated, annot.type == 'hg38_genes_exons')
unique_exons = exons [!duplicated(exons[c(1,2,3)]),]

m = merge(unique_five_utrs, unique_three_utrs, all=TRUE)

unique_exons_without_UTR = anti_join(unique_exons, m, by=c("seqnames", "start", "end", "strand"))

print("Number of three_utrs")
nrow(unique_three_utrs)

print("Number of five_utrs")
nrow(unique_five_utrs)

print("Number of Unique exons")
nrow(unique_exons_without_UTR)
