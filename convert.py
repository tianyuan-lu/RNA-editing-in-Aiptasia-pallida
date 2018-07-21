#!/usr/bin/python3

import argparse
import csv

parser = argparse.ArgumentParser(description = "convert antisense of paired-end.")
parser.add_argument('unconverted', type = argparse.FileType('r'), help = 'unconverted file.')
args = parser.parse_args()

def convert(str):
    if str == 'A': con = 'T'
    if str == 'T': con = 'A'
    if str == 'G': con = 'C'
    if str == 'C': con = 'G'
    return con

tsv = csv.reader(args.unconverted, delimiter = '\t')
for line in tsv:
    org, var = list(line[3])
    strand = line[5]
    AD, DP = line[6].split(':')
    if org not in list('ATGC'): continue
    if strand == '+':
        print(line[0], line[2], org, var, int(AD), int(DP), sep = '\t')
        continue
    if strand == '-':
        print(line[0], line[2], convert(str(org)), convert(str(var)), int(AD), int(DP), sep = '\t')
