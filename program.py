#!/usr/bin/env python2.7

import ast
import csv
import json
from reduce_bridges import *

#Read in a CSV.
with open('knots.csv') as csvfile:
    fieldnames = ['name', 'pd_notation']
    knotreader = csv.DictReader(csvfile)

    for row in knotreader:
        # Evaluate strings containing Python lists.
        knot = create_knot_from_pd_code(ast.literal_eval(row['pd_notation']), row['name'])

        print '----------------'
        print knot.name
        print 'in:  ' + str(knot)
        knot.simplify_rm1_rm2_recursively()
        print 'out: ' + str(knot)

        #print json.dumps(knot, default=ObjectEncoder)
        for crossing in knot.crossings:
            print json.dumps(crossing, default=ObjectEncoder)
        

        #print json.dumps(knot, default=ObjectEncoder)

        #with open('output.json', 'w') as outfile:
         #   json.dump(knot, outfile)
