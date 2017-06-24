#!/usr/bin/env python2.7

import ast
import csv
import json
import logging
import sys, getopt, os
from reduce_bridges import *

logging.basicConfig(filename='bridge_computation.log', filemode='w', format='%(asctime)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

def bridge_computation(argv):
    inputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["inputfile="])
    except getopt.GetoptError:
        print 'bridge_computation.py -i <inputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'bridge_computation.py -i <inputfile>'
            sys.exit()
        elif opt in ("-i", "--inputfile"):
            inputfile = arg

    # Create a directory for outputs.
    if not os.path.exists('outputs'):
        os.makedirs('outputs')

    if os.path.isdir(inputfile):
        # Traverse the directory to process all csv files.
        for root, dirs, files in os.walk(inputfile):
            for file in files:
                if file.endswith(".csv"):
                    calculate_bridge_index(os.path.join(root, file))
    elif os.path.isfile(inputfile):
        calculate_bridge_index(inputfile)
    else:
        print "The specified input is not a file or a directory. Please try a different input."
        logging.warning("The specified input is not a file or a directory. Please try a different input.")

def calculate_bridge_index(inputfile):
    # Create an output file.
    root, ext = os.path.splitext(os.path.basename(inputfile))
    outfile_name = 'outputs/' + root + '_output.csv'
    with open(outfile_name, "w") as outfile:
        outputwriter = csv.writer(outfile, delimiter=',')
        outputwriter.writerow(['name','computed_bridge_index'])

    # Read in a CSV.
    with open(inputfile) as csvfile:
        fieldnames = ['name', 'pd_notation']
        knotreader = csv.DictReader(csvfile)

        # Perform actions on each row of the input CSV.
        for row in knotreader:
            # Create a knot object.
            knot = create_knot_from_pd_code(ast.literal_eval(row['pd_notation']), row['name'])
            logging.info('Created knot ' + str(knot.name))
            logging.debug('The initial PD code of the knot is ' + str(knot))
            # Simplify the knot now to avoid choosing bridges which will be
            # discarded during simplification.
            knot.simplify_rm1_rm2_recursively()
            # Designate initial bridges.
            if (knot.num_crossings() > 1):
                knot.designate_bridge(knot.crossings[0])
                knot.designate_additional_bridge()
                # Drag crossings, simplify knot, and identify bridges
                # until all crossings belong to a bridge.
                while knot.free_crossings != []:
                    args = knot.find_crossing_to_drag()
                    if args:
                        knot.drag_crossing_under_bridge_resursively(*args)
                        knot.simplify_rm1_rm2_recursively()
                    else:
                        knot.designate_additional_bridge()
            computed_bridge_index = len(knot.bridges)
            logging.info('Finished processing ' + str(knot.name) + '. The final bridge number is ' + str(computed_bridge_index))
            logging.debug('The final PD code of ' + str(knot.name) + ' is ' + str(knot))

            # Add the results to our output file.
            try:
                with open(outfile_name, "a") as outfile:
                    outputwriter = csv.writer(outfile, delimiter=',')
                    outputwriter.writerow([knot.name, computed_bridge_index])
            except IOError:
                sys.exit('Cannot write output file. Be sure the directory "outputs" exists and is writeable.')

if __name__ == "__main__":
    bridge_computation(sys.argv[1:])
