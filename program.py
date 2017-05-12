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
        # Simplify the knot now to avoid choosing bridges which will be
        # discarded during simplification.
        knot.simplify_rm1_rm2_recursively()
        # Designate initial bridges.
        if (knot.num_crossings() > 1):
            # Designate the first crossing as a bridge.
            knot.designate_bridge(knot.crossings[0])
            print 'knot being processed is ' + str(knot.name)
            # Designate another bridge.
            knot.designate_additional_bridge()
            print 'the bridges are ' + str(knot.bridges)
            print 'the knot is ' + str(knot)
        # Add the results to our output.
        knot_output['knots'].append(knot.json())
        print '----------------------'

# Write the results to our output JSON file.
with open('output.json', mode = 'w') as outfile:
    json.dump(knot_output, outfile, indent = 2, cls = ComplexEncoder)
