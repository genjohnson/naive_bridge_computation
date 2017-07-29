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
                if knot.free_crossings != []:
                    base_knot_name = row['name']
                    directory = 'knot_trees/' + base_knot_name
                    knot.list_bridge_ts(directory, 0)
                    for subdir, dirs, files in os.walk(directory):
                        more_to_process = True
                        depth_to_process = 0
                        while more_to_process == True:
                            more_to_process = process_tree_with_depth(subdir, depth_to_process)
                            depth_to_process += 1
                        break
            except:
                print 'Failed to fully process the knot. Moving on to the next knot'
                logging.warning('Failed to fully process ' + str(knot.name) + '. Moving on to the next knot.')
                continue

def process_tree_with_depth(directory, depth):
    more_to_process = False
    for subdir, dirs, files in os.walk(directory):
        for file in files:
            # If file name ends in "_" + depth + ".csv", open the file.
            if (depth == int(file.rsplit('_', 1)[-1].rsplit('.', 1)[0])):
                file_path = os.path.join(subdir, file)
                with open(file_path) as treecsvfile:
                    treereader = csv.DictReader(treecsvfile)
                    for tree in treereader:
                        knot = create_knot_from_pd_code(ast.literal_eval(tree['pd_notation']), tree['name'], ast.literal_eval(tree['bridges']))
                        while knot.free_crossings != []:
                            try:
                                # Drag underpasses & simplify until no moves are possible.
                                args = knot.find_crossing_to_drag()
                                knot.drag_crossing_under_bridge_resursively(*args)
                                knot.simplify_rm1_rm2_recursively()
                            except:
                                break
                        if knot.free_crossings == []:
                            # @todo Write number of bridges to output file.
                            print 'Number of bridges for ' + knot.name + ' is ' + str(len(knot.bridges))
                            # computed_bridge_index = len(knot.bridges)
                            # logging.info('Finished processing ' + str(knot.name) + '. The final bridge number is ' + str(computed_bridge_index))
                            # logging.debug('The final PD code of ' + str(knot.name) + ' is ' + str(knot))
                            # # Add the results to our output file.
                            # try:
                            #     with open(outfile_name, "a") as outfile:
                            #         outputwriter = csv.writer(outfile, delimiter=',')
                            #         outputwriter.writerow([knot.name, computed_bridge_index])
                            # except IOError:
                            #     sys.exit('Cannot write output file. Be sure the directory "outputs" exists and is writeable.')
                        else:
                            knot.list_bridge_ts(subdir, depth + 1)
                            more_to_process = True
    return more_to_process

if __name__ == "__main__":
    bridge_computation(sys.argv[1:])
