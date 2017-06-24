#!/usr/bin/env python2.7

import csv, getopt, numpy, os, sys

def write_analysis_output(argv):
	"""
	Return the minimum bridge index returned by bridge_computation.py.
	"""
	input_source = ''
	output_dir = 'analyzed_output'
	try:
		opts, args = getopt.getopt(argv,"hi:o:",["input_source=", "output_dir",])
	except getopt.GetoptError:
		print 'bridge_computation.py -i <input_source> -o <output_dir>'
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print 'bridge_computation.py -i <input_source> -o <output_dir>'
			sys.exit()
		elif opt in ("-i", "--input_source"):
			input_source = arg
		elif opt in ("-o", "--output_dir"):
			output_dir = arg
	# Create a file for output.
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)

	outfile_path = output_dir + '/minimum_computed_bridge_indices.csv'

	with open(outfile_path, "w") as outfile:
		outputwriter = csv.writer(outfile, delimiter=',')
		outputwriter.writerow(['knot','minimum_computed_bridge_index'])

	if os.path.isdir(input_source):
		# Traverse the directory to process all csv files.
		for root, dirs, files in os.walk(input_source):
			for file in files:
				if file.endswith(".csv"):
					find_minimum_computed_bridge_index(os.path.join(root, file), outfile_path)
	elif os.path.isfile(input_source):
		find_minimum_computed_bridge_index(input_source, outfile_path)
	else:
		print "The specified input is not a file or a directory. Please try a different input."
		logging.warning("The specified input is not a file or a directory. Please try a different input.")

def find_minimum_computed_bridge_index(csv_file, outfile_path):
	computed_bridge_indexes = numpy.loadtxt(fname=csv_file, skiprows=1, usecols=(1,), delimiter=',', dtype=int)
	min_computed_bridge_index = min(computed_bridge_indexes)
	root, ext = os.path.splitext(os.path.basename(csv_file))
	knot_name = root[:-7]
	with open(outfile_path, "a") as outfile:
		outputwriter = csv.writer(outfile, delimiter=',')
		outputwriter.writerow([knot_name,min_computed_bridge_index])	

if __name__ == "__main__":
	write_analysis_output(sys.argv[1:])
