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
        # Simplify the knot.
        knot.simplify_rm1_rm2_recursively()
        # Add the results to our output.
        knot_output['knots'].append(knot.json())
        # Output a message that the knot has been processed.
        print 'processed ' + knot.name

# Write the results to our output JSON file.
with open('output.json', mode='w') as outfile:
    json.dump(knot_output, outfile, indent=2, cls=ComplexEncoder)
