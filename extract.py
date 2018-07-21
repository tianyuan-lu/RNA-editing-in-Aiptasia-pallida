#!/usr/bin/python3

import csv
import argparse

parser = argparse.ArgumentParser(description = "extract gene ID and regions")
parser.add_argument('file', type = argparse.FileType('r'), help = "SnpEff annotated vcf file")
args = parser.parse_args()

tsv = csv.reader(args.file, delimiter = '\t')
for row in tsv:
   
    region = list(row[7].split('|'))[1]
    ID = list(row[7].split('|'))[4]
    
    print(row[0], row[1], row[3], row[4], region, ID, sep = '\t')
