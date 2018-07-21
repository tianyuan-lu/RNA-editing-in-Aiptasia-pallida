#!/usr/bin/python3

import csv
import argparse

parser = argparse.ArgumentParser(description="""Given tab-separated files""")
parser.add_argument('cov_files1',
                    type=argparse.FileType('r'),
                    help="List of coverage.")
parser.add_argument('cov_files2',
                    type=argparse.FileType('r'),
                    help="List of variants.")
args = parser.parse_args()

dict = {}
for line in csv.reader(args.cov_files1, delimiter = '\t'):
    scaf = line[0]
    if scaf not in dict:
        dict[scaf] = {}
    # dict[scaf][line[1]] = [line[2], line[3], line[4], line[5], line[6], line[7], line[8], line[9], line[10], line[11], line[12], line[13]]
    dict[scaf][line[1]] = [line[i] for i in range(2, len(line))]

for line in csv.reader(args.cov_files2, delimiter = '\t'):
    if line[0] in dict:
        if line[1] in dict[line[0]]:
            for i in range(4, 15, 2):
                if line[i] == '': 
                    
                    if dict[line[0]][line[1]][int(i/2)-2] == '':
                        line[i] = '-1'
                        line[i+1] = '10000'
                        continue
                    line[i] = '0'
                    line[i+1] = '10000'        
            print('\t'.join(line))
