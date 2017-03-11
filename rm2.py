#!/usr/bin/env python2.7

import ast
import csv

def check_rm2(knot):
    """Inspect a knot for crossings that can be eliminated
    by Reidemeister moves of type 2.

    >>> check_rm2([[1, 2, 3, 4], [1, 3, 2, 4]])
    an overlay exists
    >>> check_rm2([[1, 2, 3, 4], [3, 1, 2, 4]])
    no overlay exists

    Arguments:
    knot -- the PD notation of a knot
    """

    for i in range(0, len(knot)-1):
        if knot[i][1] == knot[i+1][2] and knot[i][2] == knot[i+1][1]:
            print 'an overlay exists'
        else:
            print 'no overlay exists'

# Read in a CSV.
with open('knots.csv') as csvfile:
    fieldnames = ['name', 'pd_notation']
    knotreader = csv.DictReader(csvfile)

    for row in knotreader:
        # Evaluate strings containing Python lists.
        knot = ast.literal_eval(row['pd_notation'])
        # Check if the knot contains any overlays.
        check_rm2(knot)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
