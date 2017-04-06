#!/usr/bin/env python2.7

import ast
import csv
from rm2 import *

class Crossing:
    def __init__(self, pd_code, bridge):
        self.pd_code = pd_code
        self.bridge = bridge

    def __eq__(self, other):
        return self.pd_code == other.pd_code and self.bridge == other.bridge

    def alter_elements_greater_than(self, value, addend):
        """
        Change the value of all elements in a Crossing which are greater
        than the provided value.

        Arguments:
        value -- (int) The number to compare each element of the crossing with.
        addend -- (int) The number to add to crossing elements greater than value.
        """
        self.pd_code = [x+addend if x > value else x for x in self.pd_code]
        return self

    def has_duplicate_value(self):
        """
        Determine if there are duplicate values in the PD notation of a crossing.
        """
        sets = reduce(
            lambda (u, d), o : (u.union([o]), d.union(u.intersection([o]))),
            self.pd_code,
            (set(), set()))
        if sets[1]:
            return list(sets[1])[0]
        else:
            return False

class Knot:
    def __init__(self, crossings):
        self.crossings = crossings # crossings is a list of Crossing objects

    def __eq__(self, other):
        return self.crossings == other.crossings

    def __str__(self):
        return str([crossing.pd_code for crossing in self.crossings])

    def has_rm1(self):
        """
        Inspect a knot for crossings that can be eliminated
        by Reidemeister moves of type 1.
        """
        twisted_crossings = []
        for index, crossing in enumerate(self.crossings):
            if crossing.has_duplicate_value():
                twisted_crossings.append(index)
        if twisted_crossings:
            return twisted_crossings
        else:
            return False

    def remove_crossings(self, indices):
        """
        Remove crossings from a knot.

        Arguments:
        indices -- (list) the indices of the crossings to remove
        """
        # Remove crossings from last to first to avoid changing
        # the index of crossings not yet processed.
        indices.sort(reverse = True)
        for index in indices:
            del self.crossings[index]   
        return self

    def simplify_rm1(self, twisted_crossings):
        """
        Simplify one level of a knot by Reidemeister moves of type 1.

        Arguments:
        twisted_crossings -- (list) the indices of crossings to eliminate
        """
        crossings = self.crossings
        for index in twisted_crossings:
            duplicate_value = self.crossings[index].has_duplicate_value()
            for crossing in knot.crossings:
                crossing.alter_elements_greater_than(duplicate_value, -2)
        self.remove_crossings(twisted_crossings)
        return self

    def simplify_rm1_recursivly(self):
        """
        Simplify a knot by Reidemeister moves of type 1 until
        no more moves are possible.

        >>> simplify_rm1_recursive([[1, 5, 2, 4], [3, 3, 4, 2], [6, 6, 7, 5], [8, 8, 1, 7]])
        []
        >>> simplify_rm1_recursive([[1, 5, 2, 4], [3, 3, 4, 2], [7, 10, 8, 1], [8, 6, 9, 5], [9, 6, 10, 7]])
        [[3, 6, 4, 1], [4, 2, 5, 1], [5, 2, 6, 3]]
        """
        while True:
            moves_possible = self.has_rm1()
            if moves_possible:
                self.simplify_rm1(moves_possible)
            if not moves_possible:
                break
        return self

def simplify_rm1_rm2_recursivly(knot):
    """
    Simplify a knot by Reidemeister moves of types 1 & 2 until
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

        print str(row['name'])
        print knot

        #simplify_rm1_rm2_recursivly(knot)
        knot.simplify_rm1_recursivly()
            
        print knot

# if __name__ == '__main__':
#     import doctest
#     doctest.testmod()
