#!/usr/bin/env python2.7

import ast
import csv
from collections import deque
from reduce_bridges import alter_if_greater

def generate_pd_code_varients(pd_code):
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

def bulk_generate_pd_codes(in_file = 'knots.csv', out_file = 'pd_codes/pd_codes.csv', reverse = True):
	"""
	Create a csv of all PD code variations of a knot.

	Arguments:
	in_file -- (str) The name of the file contaning PD codes to process.
	out_file -- (str) The name of the file to write the results.
	reverse -- (bool) Generate PD codes of the knot with reverse orientation.
	"""
	infile = open(in_file, "r")
	reader = csv.DictReader(infile)
	outfile = open(out_file, "w")
	writer = csv.writer(outfile, delimiter=',')
	writer.writerow(['name','pd_notation'])

	for row in reader:
		original_pd_code = ast.literal_eval(row['pd_notation'])
		i = 0
		pd_codes = generate_pd_code_varients(original_pd_code)
		for pd_code in pd_codes:
			name = row['name'] + '_' + str(i)
			i+=1
			writer.writerow([name, pd_code])
		if reverse:
			reverse_pd_code = reverse_orientation(original_pd_code)
			pd_codes = generate_pd_code_varients(reverse_pd_code)
			for pd_code in pd_codes:
				name = row['name'] + '_reversed_' + str(i)
				i+=1
				writer.writerow([name, pd_code])
	infile.close()
	outfile.close()

def reverse_orientation(pd_code):
	"""
	Reverse the orientation of a PD code.

	Arguments:
	pd_code -- (list) A PD code expressed as a list of lists.
	"""
	max_value = len(pd_code)*2

	def reverse_element(x):
		x = max_value+2-x
		if (x > max_value):
			x = x%max_value
		return x

	def reverse_crossing(crossing):
		# Change the order of the elements in the crossing.
		crossing = deque(crossing)
		crossing.rotate(2)
		crossing = list(crossing)
		# Change the value of each element in the crossing.
		crossing = map(reverse_element, crossing)
		return crossing

	pd_code.reverse()
	pd_code = [reverse_crossing(crossing) for crossing in pd_code]
	return pd_code

bulk_generate_pd_codes()
