#!/usr/bin/env python3

"""
>bonafideRNA.py<
"""

import csv
import glob
import gzip
import statistics
import sys
import argparse
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("file", type = argparse.FileType('r'), help = "file to be bonafide corrected.")
args = parser.parse_args()
def lazy_int(string):
    string = string.strip()
    return int(string) if string else 0

def calc_cols(input_list):
    return sum([1 for x in input_list if x])

tsv_reader = csv.reader(args.file, delimiter='\t')
for row in tsv_reader:
    if not row: continue

    per_sample_cov = [lazy_int(i) for i in row[5::2]]
    per_sample_editing = [lazy_int(j) for j in row[4::2]]
    
    # criteria I: editing > 0 for all replicates
    if not all(per_sample_editing): continue

    # criteria I: presence in at least 2 replicats
    # if per_sample_cov.count(0) > 2: continue

    # criteria II: median coverage >= 5
    if not statistics.median(x for x in per_sample_cov if x > 0) >= 5: continue
    
    # criteria III: mean coverage >= 10
    if not statistics.mean(x for x in per_sample_cov if x > 0) >=10: continue

    print('\t'.join(row))
