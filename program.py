#!/usr/bin/env python2.7

import ast
import csv
from reduce_bridges import *

#Read in a CSV.
with open('knots.csv') as csvfile:
    fieldnames = ['name', 'pd_notation']
    knotreader = csv.DictReader(csvfile)

    for row in knotreader:
        # Evaluate strings containing Python lists.
        knot = Knot([Crossing(pd_code) for pd_code in ast.literal_eval(row['pd_notation'])])

        print str(row['name'])
        print knot
        knot.simplify_rm1_rm2_recursively()
        print knot
