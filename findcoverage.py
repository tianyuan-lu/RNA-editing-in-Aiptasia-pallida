#!/usr/bin/python3

import argparse
import csv

parser = argparse.ArgumentParser(description="""Given tab-separated files""")
parser.add_argument('cov_files1',
                    type=argparse.FileType('r'),
                    help="Coverage.")
parser.add_argument('cov_files2',
                    type=argparse.FileType('r'),
                    help="Variant.")
args = parser.parse_args()

ref = {}
tsv = csv.reader(args.cov_files2, delimiter = '\t')
for line in tsv:
    scaf = line[0]
    if scaf not in ref:
        ref[scaf] = {}
    pos = line[1]
    ref[scaf][pos] = 0

tsv = csv.reader(args.cov_files1, delimiter = '\t')
for line in tsv:
    if line[0] in ref:
        if line[1] in ref[line[0]]:
            print('\t'.join(line))
