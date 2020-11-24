#!/usr/bin/python

import sys, os, glob

pbs_email = input("Enter email to use as PBS user email.")
my_dir = input("Enter working directory (where the output directory will be created and output scripts)")
output = input("Enter output folder name (will also prefix files with this name)")
genome_path = input("Enter the path to the genome .fa file.")
basecall_path = input("Enter the path to the basecalled reads fastq/fastq.gz file.")

my_dir = os.path.abspath(my_dir)
genome_path = os.path.abspath(genome_path)
basecall_path = os.path.abspath(basecall_path)

if not os.path.isfile(genome_path):
  raise Exception(f"{genome_path} is not a valid path (genome .fa path)")

if not os.path.isfile(basecall_path):
  raise Exception(f"{basecall_path} is not a valid path (basecalled reads fastq/fastq.gz file)")

if not os.path.isdir(my_dir):
  raise Exception(f"{my_dir} is not a valid directory (working directory)")

if os.path.isdir(f"{my_dir}/{output}"):
  raise Exception(f"{my_dir}/{output} already exists. Please remove it or change the output folder name.")

print(f"Generating scripts for {output}...")

output_path = my_dir + "/" + output
script_path = output_path = "/" + "epinano_scripts"

os.mkdir(output_path)
os.mkdir(script_path)
os.mkdir(output_path + "/" + "mapped")

with open(f"{script_path}/Step_1_Align_Index.pbs", "w") as f:
  f.writelines([
    "#!/bin/bash",
    "#PBS -N epinano_1_align", 
    "#PBS -l nodes=1:ppn=8,mem=64gb,walltime=11:59:00",
    "#PBS -j oe",
    "#PBS -m ae",
    f"#PBS -M {pbs_email}"
    "set -e",
    "module load minimap2/2.17",
    "module load samtools/1.10",
    f"cd {output_path}/mapped",
    f"minimap2 --MD -t 6 -ax splice -k14 -uf {genome_path} {basecall_path} > {output}_aln.sam",
    f"samtools view -hbS -F 3844 {output_path}/mapped/{output}_aln.sam | samtools sort -@ 6 -o sorted_{output}.bam",
    f"bamtools split -in {output_path}/mapped/sorted_{output}.bam -reference",
    f"ls {output_path}/mapped/sorted_{output}.REF_*.bam | xargs -n1 -P5 samtools index"
  ])

############### Generating Step_2_Error_Feature_Table scripts ###############

step2path = script_path + "/" + "Step_2_Error_Feature_Table"
os.mkdir(step2path)

count=0
file_count=0
batch_size=2 # Change this to the number of Epinano_Variant's you want run in each job.
f = None

for file in glob.glob(f"{output_path}/mapped/sorted_{output}.REF_*.bam"):
  if count % batch_size == 0 or count == 0:
    file_count += 1
    if f:
      f.close()
    f = open(f"{step2path}/{file_count}.pbs", "w")
    f.writelines([
      "#!/bin/bash",
      "#PBS -N epinano2featuretable", 
      "#PBS -l nodes=1:ppn=8,mem=64gb,walltime=11:59:00",
      "#PBS -j oe",
      "#PBS -m ae",
      f"#PBS -M {pbs_email}"
      "set -e",
      "module load samtools/1.10",
      f"source {my_dir}/epinano1/bin/activate"
    ])

  f.write(f"python3 {epinano_dir}/Epinano_Variants.py -n 6 -R {genome_path} -b {file} -s {epinano_dir}/misc/sam2tsv.jar --type g")
  count += 1

if f:
  f.close()

############### Generating Step_3_5mer scripts ###############

step3path = script_path + "/" + "Step_3_5mer"
os.mkdir(step3path)

count=0
file_count=0
batch_size=2 # Change this to the number of Sliding Windows's you want run in each job.
f = None

for file in glob.glob(f"{output_path}/mapped/*per.site.var.csv"):
  if count % batch_size == 0 or count == 0:
    file_count += 1
    if f:
      f.close()
    f = open(f"{step3path}/{file_count}.pbs", "w")
    f.writelines([
      "#!/bin/bash",
      "#PBS -N epinano3slide", 
      "#PBS -l nodes=1:ppn=8,mem=64gb,walltime=11:59:00",
      "#PBS -j oe",
      "#PBS -m ae",
      f"#PBS -M {pbs_email}"
      "set -e",
      "module load samtools/1.10",
      f"source {my_dir}/epinano1/bin/activate"
    ])

  f.write(f"python3 {epinano_dir}/Slide_Variants.py {file} 5")
  count += 1

if f:
  f.close()

############### Generating Step_4_Prediction scripts ###############

step4path = script_path + "/" + "Step_4_Prediction"
os.mkdir(step4)

count=0
file_count=0
batch_size=2 # Change this to the number of Sliding Windows's you want run in each job.
f = None

for file in glob.glob(f"{output_path}/mapped/sorted_{output}.REF_*.5mer.csv"):
  if count % batch_size == 0 or count == 0:
    file_count += 1
    if f:
      f.close()
    f = open(f"{step4path}/{file_count}.pbs", "w")
    f.writelines([
      "#!/bin/bash",
      "#PBS -N epinano_1_align", 
      "#PBS -l nodes=1:ppn=8,mem=64gb,walltime=11:59:00",
      "#PBS -j oe",
      "#PBS -m ae",
      f"#PBS -M {pbs_email}"
      "set -e",
      "module load samtools/1.10",
      f"source {my_dir}/epinano2/bin/activate"
    ])

  f.writelines([
    # Filter non-RRACH motifs into new file.
    f"old_header=$(head -n 1 {file[:-3]})",
    f"egrep '[AG][AG]AC[ACT]' {file[:-3]} > {file[:-3]}_RRACH_filtered.csv",
    f'sed -i "1s/^/$old_header\n/" {file[:-3]}_RRACH_filtered.csv',
    f"python3 {epinano_dir}/Epinano_Predict.py \
    --model {epinano_dir}/models/rrach.q3.mis3.del3.linear.dump \
    --predict {file[:-3]}_RRACH_filtered.csv \
    --columns 8,13,23 \
    --out_prefix {file}_prediction"
  ])
  count += 1

if f:
  f.close()

