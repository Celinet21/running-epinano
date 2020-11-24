#!/usr/bin/env python3
import sys
import os

file_path = sys.argv[1]

output_name = sys.argv[2]

if not os.path.isfile(file_path):
    print("File path {} does not exist. Exiting...".format(file_path))
    sys.exit()

with open(file_path, "r") as f:
  output = open(output_name, "w")
  for line in f:

    split = line.split(",")
    chrom = split[2]
    start = str(int(split[1].split("-")[0]) - 1)
    end = split[1].split("-")[1]
    
    name = "m6a-" + split[25]
    score = split[27]
    strand = split[3]

    output.write(chrom + "\t" + start + "\t" + end + "\t" + name + "\t" + score + "\t" + strand + "\n")

  output.close()
