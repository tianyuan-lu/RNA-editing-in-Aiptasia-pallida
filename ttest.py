#!/usr/bin/env python3

"""
>t.test<
"""

import argparse
import csv
import sys
import numpy
import natural_sort
from scipy import stats

parser = argparse.ArgumentParser(description="""Given tab-separated files""")
parser.add_argument('cov_files1',
                    type=argparse.FileType('r'),         
                    help="List of tab-separated files.")
parser.add_argument('cov_files2',
                    type=argparse.FileType('r'),
                    help="List of tab-separated files.")
parser.add_argument('-v', action='store_true',
                    help="verbose mode, prints progress to stderr.")
args = parser.parse_args()

print("scaffold", "position", "origin", "variant", "average1", "average2", "difference", "CV1", "CV2", "trend", "p-value", sep = '\t')

#to combined_data[scaffold][1-based_coord] = [total, variant]
combined_data = {}
counter_rows = 0
tsv_reader = csv.reader(args.cov_files1, delimiter='\t')
for row in tsv_reader:
    if not row: continue

    if args.v:
        counter_rows += 1
        if counter_rows % 1000000 == 0:
            print ('{} rows processed...'.format(counter_rows),
                   file=sys.stderr)

    scaf = row[0]
    if scaf not in combined_data: combined_data[scaf] = {}

    pos = int(row[1])    
    # combined_data[scaf][pos] = [row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15]]
    combined_data[scaf][pos] = [row[i] for i in range(2, len(row))]
combined_data2 = {}
counter_rows = 0
tsv_reader = csv.reader(args.cov_files2, delimiter='\t')
for row in tsv_reader:
    if not row: continue

    if args.v:
        counter_rows += 1
        if counter_rows % 1000000 == 0:
            print ('{} rows processed...'.format(counter_rows),
                   file=sys.stderr)

    scaf = row[0]
    if scaf not in combined_data2: combined_data2[scaf] = {}

    pos = int(row[1])
    # combined_data2[scaf][pos] = [row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15]]
    combined_data2[scaf][pos] = [row[i] for i in range(4, len(row))]
#to print
for scaf in natural_sort.natural_sort(combined_data):
    if scaf in combined_data2: 
        for pos in sorted(combined_data[scaf]):
            if pos in combined_data2[scaf]:
        # recalculate var % from the new total numbers
                origin = combined_data[scaf][pos][0]
                variant = combined_data[scaf][pos][1]
                data1 = ()
                for i in range(2,14,2):
                    prc = int(combined_data[scaf][pos][i])/int(combined_data[scaf][pos][i+1])
                    if prc > 0: data1 = data1 + (prc,)
                data2 = ()
                for i in range(0,12,2):
                    prc = int(combined_data2[scaf][pos][i])/int(combined_data2[scaf][pos][i+1])
                    if prc > 0: data2 = data2 + (prc,)
                D1 = numpy.mean(data1)
                CV1 = stats.variation(data1)
                D2 = numpy.mean(data2)
                CV2 = stats.variation(data2)
                if D1 <= 0.95 and D1 >= 0.05 and D2 <= 0.95 and D2 >= 0.05:
                    stat, p = stats.ttest_ind(data1, data2, equal_var = False)
                    if stat<0: trend = 'up'
                    if stat>0: trend = 'down'
                    print (scaf, pos, origin, variant, D1, D2, abs(D1-D2), CV1, CV2, trend, p, sep='\t')
