#!/usr/bin/env python2.7

import ast
import csv
from rm1 import *
from rm2 import *

class Crossing:
    def __init__(self, pd_code, bridge):
        self.pd_code = pd_code
        self.bridge = bridge

class Knot:
    def __init__(self, crossings):
        self.crossings = crossings # crossings is a list of Crossing objects
        self.pd_notation = [crossing.pd_code for crossing in self.crossings]

def simplify_rm1_rm2_recursivly(knot):
    """Simplify a knot by Reidemeister moves of types 1 & 2 until
    no more moves are possible.

    >>> simplify_rm1_rm2_recursivly([[1,7,2,6],[2,9,3,10],[5,1,6,10],[7,5,8,4],[8,3,9,4]])
    []

    Arguments:
    knot -- the PD notation of a knot
    """
    while True:
        if check_rm1(knot):
            simplify_rm1_recursive(knot)
        if check_rm2(knot):
            simplify_rm2_recursive(knot)
        if not check_rm1(knot) and not check_rm2(knot):
            break;
    return knot

# Read in a CSV.
with open('knots.csv') as csvfile:
    fieldnames = ['name', 'pd_notation']
    knotreader = csv.DictReader(csvfile)

    for row in knotreader:
        # Evaluate strings containing Python lists.
        knot = Knot([Crossing(pd_code, 0) for pd_code in ast.literal_eval(row['pd_notation'])])

        print str(row['name']) +': the original knot is ' + str(knot.pd_notation)

        check_rm1(knot)
        #simplify_rm1_rm2_recursivly(knot)

        print str(row['name']) +': the final knot is ' + str(knot.pd_notation)

# if __name__ == '__main__':
#     import doctest
#     doctest.testmod()
