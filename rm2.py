#!/usr/bin/env python2.7

import ast
import csv

def check_rm2(knot):
    """Inspect a knot for crossings that can be eliminated
    by Reidemeister moves of type 2.

    >>> check_rm2([[1, 2, 3, 4], [1, 3, 2, 4], [5, 6, 7, 8], [7, 5, 6, 8]])
    ([0, 1], [2, 3])
    >>> check_rm2([[1, 2, 3, 4], [3, 1, 2, 4], [5, 6, 7, 8], [5, 7, 6, 8]])
    ([0, 1], [3, 4])
    >>> check_rm2([[1, 2, 3, 4], [1, 2, 3, 4]])
    False

    Arguments:
    knot -- the PD notation of a knot
    """
    overlayed_crossings = []
    removed_segments = []
    for i in range(0, len(knot)-1):
        if knot[i][1] == knot[i+1][2] and knot[i][2] == knot[i+1][1]:
            overlayed_crossings = [i, i+1]
            removed_segments = [knot[i][1], knot[i][2]]
            return (overlayed_crossings, removed_segments)
        elif knot[i][2] == knot[i+1][0] and knot[i][3] == knot[i+1][3]:
            overlayed_crossings = [i, i+1]
            removed_segments = [knot[i][2], knot[i][3]]
            return (overlayed_crossings, removed_segments)
    else:
        return False

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
