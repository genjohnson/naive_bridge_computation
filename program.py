#!/usr/bin/env python2.7

import ast
import csv
import json
import logging
from reduce_bridges import *

logging.basicConfig(filename='naive_bridges.log', format='%(asctime)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

# Stub for our output JSON file.
knot_output = {"knots":[]}

# Read in a CSV.
with open('knots.csv') as csvfile:
    fieldnames = ['name', 'pd_notation']
    knotreader = csv.DictReader(csvfile)

    # Perform actions on each row of the input CSV.
    for row in knotreader:
        # Create a knot object.
        knot = create_knot_from_pd_code(ast.literal_eval(row['pd_notation']), row['name'])
        logging.info('Created knot ' + str(knot.name))
        logging.debug('The initial PD code of the knot is ' + str(knot))
        print 'Knot name is ' + str(knot.name)
        # Simplify the knot now to avoid choosing bridges which will be
        # discarded during simplification.
        knot.simplify_rm1_rm2_recursively()
        # Designate initial bridges.
        if (knot.num_crossings() > 1):
            knot.designate_bridge(knot.crossings[0])
            knot.designate_additional_bridge()
            # Drag crossings, simplify knot, and identify bridges
            # until all crossings belong to a bridge.
            knot.find_crossing_to_drag()
            while knot.free_crossings != []:
                args = knot.find_crossing_to_drag()
                if args:
                    knot.drag_crossing_under_bridge_resursively(*args)
                    knot.simplify_rm1_rm2_recursively()
                else:
                    knot.designate_additional_bridge()
        logging.info('Finished processing ' + str(knot.name))
        logging.debug('The final PD code of ' + str(knot.name) + ' is ' + str(knot))

        # Add the results to our output.
        print '========================='
        #print 'The final bridge number of ' + str(knot.name) + ' is ' + str(len(knot.bridges))
        knot_output['knots'].append(knot.json())

# Write the results to our output JSON file.
with open('output.json', mode = 'w') as outfile:
    json.dump(knot_output, outfile, indent = 2, cls = ComplexEncoder)
