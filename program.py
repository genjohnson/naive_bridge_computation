#!/usr/bin/env python2.7

import ast
import csv
import json
from reduce_bridges import *

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
        print 'knot being processed is ' + str(knot.name)
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
                drag_info = knot.find_crossing_to_drag()
                if drag_info:
                    knot.drag_crossing_under_bridge(drag_info[2], drag_info[3])
                    knot.simplify_rm1_rm2_recursively()
                else:
                    knot.designate_additional_bridge()
        else:
            print 'after simplifying, the knot is the unknot'
        # Add the results to our output.
        knot_output['knots'].append(knot.json())
        print '----------------------'

# Write the results to our output JSON file.
with open('output.json', mode = 'w') as outfile:
    json.dump(knot_output, outfile, indent = 2, cls = ComplexEncoder)
