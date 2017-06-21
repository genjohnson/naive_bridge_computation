#!/usr/bin/env python2.7

import os
import sys
import getopt

def bulk_bridge_computation(argv):
	indirectory = ''
	try:
		opts, args = getopt.getopt(argv,"hi:o:",["indirectory="])
	except getopt.GetoptError:
		print 'bulk_bridge_computation.py -i <indirectory>'
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print 'bulk_bridge_computation.py -i <indirectory>'
			sys.exit()
		elif opt in ("-i", "--indirectory"):
			indirectory = arg
	
	# Traverse a directory to find all csv files.
	for root, dirs, files in os.walk(indirectory):
		for file in files:
			if file.endswith(".csv"):
				print(os.path.join(root, file))

if __name__ == "__main__":
	bulk_bridge_computation(sys.argv[1:])
