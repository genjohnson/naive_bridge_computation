#!/usr/bin/env python2.7

import ast
import csv
from reduce_bridges import alter_if_greater

def generate_all_pd_codes(pd_code):
	"""
	Generate a list of all PD code variations for a given PD code.

	Arguments:
	pd_code -- (list) A PD code expressed as a list of lists.
	"""
	max_value = len(pd_code)*2
	passes = max_value-1
	pd_codes = [pd_code[:]]
	while (passes > 0):
		for i, crossing in enumerate(pd_code):
			pd_code[i] = [alter_if_greater(x, 0, 1, max_value) for x in crossing]
		pd_codes.append(pd_code[:])
		passes-=1
	return pd_codes

generate_all_pd_codes([[2,5,3,6],[4,1,5,2],[6,3,1,4]])

def bulk_generate_pd_codes(in_file = 'knots.csv', out_file = 'pd_codes.csv'):
	infile = open(in_file, "r")
	reader = csv.DictReader(infile)
	outfile = open(out_file, "w")
	writer = csv.writer(outfile, delimiter=',')
	for row in reader:
		i = 0
		pd_codes = generate_all_pd_codes(ast.literal_eval(row['pd_notation']))
		for pd_code in pd_codes:
			name = row['name'] + '_' + str(i)
			i+=1
			writer.writerow([name, pd_code])
	infile.close()
	outfile.close()
bulk_generate_pd_codes()
