#!/usr/bin/env python2.7

import ast
import csv
import json
import logging
import sys, getopt, os
from reduce_bridges import *

logging.basicConfig(filename='bridge_computation.log', filemode='w', format='%(asctime)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

def bridge_computation(argv):
    inputfile = ''
    outputdir = 'output'
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["inputfile=", "outputdir",])
    except getopt.GetoptError:
        print 'bridge_computation.py -i <inputfile> -o <outputdir>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'bridge_computation.py -i <inputfile> -o <outputdir>'
            sys.exit()
        elif opt in ("-i", "--inputfile"):
            inputfile = arg
        elif opt in ("-o", "--outputdir"):
            outputdir = arg

    # Create a directory for outputs.
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)

    if os.path.isdir(inputfile):
        # Traverse the directory to process all csv files.
        for root, dirs, files in os.walk(inputfile):
            for file in files:
                if file.endswith(".csv"):
                    try:
                        calculate_bridge_index(os.path.join(root, file), outputdir)
                    except:
                        logging.error('Failed to fully process ' + str(file))
                        print 'Failed to fully process ' + str(file)
    elif os.path.isfile(inputfile):
        calculate_bridge_index(inputfile, outputdir)
    else:
        print "The specified input is not a file or a directory. Please try a different input."
        logging.warning("The specified input is not a file or a directory. Please try a different input.")

def calculate_bridge_index(inputfile, outputdir):
    # Read in a CSV.
    with open(inputfile) as csvfile:
        fieldnames = ['name', 'pd_notation']
        knotreader = csv.DictReader(csvfile)

        # Perform actions on each row of the input CSV.
        for row in knotreader:
            # Create a file to store the output of all trees of this knot.
            outfile_name = outputdir + '/' + row['name'] + '_output.csv'
            with open(outfile_name, "w") as outfile:
                outputwriter = csv.writer(outfile, delimiter=',')
                outputwriter.writerow(['name','computed_bridge_index'])
            try:
                # Create a knot object.
                knot = create_knot_from_pd_code(ast.literal_eval(row['pd_notation']), row['name'])
                logging.info('Processing knot ' + str(knot.name))
                logging.debug('The initial PD code of the knot is ' + str(knot))
                # Simplify the knot now to avoid choosing bridges which will be
                # discarded during simplification.
                knot.simplify_rm1_rm2_recursively()
                base_knot_name = row['name']
                knot.list_bridge_ts(base_knot_name)

                for subdir, dirs, files in os.walk('knot_trees/' + base_knot_name):
                    more_branches_to_process = 1
                    depth_to_process = 0
                    while (more_branches_to_process > 0):
                        more_branches_to_process = 0
                        next_depth_to_process = depth_to_process + 1
                        for file in files:
                            # If file name ends in "_" + depth_to_process + ".csv", open the file.
                            if (depth_to_process == int(file.rsplit('_', 1)[-1].rsplit('.', 1)[0])):
                                file_path = os.path.join(subdir, file)
                                with open(file_path) as treecsvfile:
                                    treereader = csv.DictReader(treecsvfile)
                                    for tree in treereader:
                                        # @todo: Configure create_knot_from_pd_code()
                                        # to take bridges arg.
                                        knot = create_knot_from_pd_code(ast.literal_eval(tree['pd_notation']), tree['name'])
                                        print knot.name
                                        while knot.free_crossings != []:
                                            try:
                                                # Drag underpasses & simplify recursively
                                                # until no more moves are possible.
                                                args = knot.find_crossing_to_drag()
                                                knot.drag_crossing_under_bridge_resursively(*args)
                                                knot.simplify_rm1_rm2_recursively()
                                            except:
                                                logging.info('We need to identify next choices for bridge Ts')
                                                print 'We need to identify next choices for bridge Ts for ' + knot.name
                                                more_branches_to_process += 1
                                                # @todo: run knot.list_bridge_ts() where tree_directory = subdir.
                                                # @todo: Write all knots/bridge choices for each depth in the same file. E.g., tree_1_1, tree_1_2, etc.
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
                        depth_to_process = next_depth_to_process
            except:
                print 'Failed to fully process the knot. Moving on to the next knot'
                logging.warning('Failed to fully process ' + str(knot.name) + '. Moving on to the next knot.')
                continue

if __name__ == "__main__":
    bridge_computation(sys.argv[1:])
