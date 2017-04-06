#!/usr/bin/env python2.7

import ast
import csv
import itertools
from itertools import izip, islice
import numpy
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

    def num_crossings(self):
        """
        Return the number of crossings in the knot.
        """
        return len(knot.crossings)

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
            for crossing in self.crossings:
                crossing.alter_elements_greater_than(duplicate_value, -2)
        self.remove_crossings(twisted_crossings)
        return self

    def simplify_rm1_recursively(self):
        """
        Simplify a knot by Reidemeister moves of type 1 until
        no more moves are possible.
        """
        while True:
            moves_possible = self.has_rm1()
            if moves_possible:
                self.simplify_rm1(moves_possible)
            if not moves_possible:
                break
        return self
     
    def has_rm2(self):
        """
        Inspect a knot for crossings that can be eliminated
        by Reidemeister moves of type 2.
        """

        # for each crossing in the knot, if the next crossing matches one of 
        # our two comparissions, then RM2 exists.



        overlayed_crossings = []
        removed_segments = []
        for i in range(0, len(knot)-1):
            if knot[i].pd_code[1] == knot[i+1].pd_code[2] and knot[i].pd_code[2] == knot[i+1].pd_code[1]:
                overlayed_crossings = [i, i+1]
                removed_segments = [knot[i].pd_code[1], knot[i].pd_code[2]]
                return (overlayed_crossings, removed_segments)
            elif knot[i].pd_code[2] == knot[i+1].pd_code[0] and knot[i].pd_code[3] == knot[i+1].pd_code[3]:
                overlayed_crossings = [i, i+1]
                removed_segments = [knot[i].pd_code[2], knot[i].pd_code[3]]
                return (overlayed_crossings, removed_segments)
        else:
            return False


def compare_two_crossings(crossing_a, crossing_b):
    if crossing_a.pd_code[1] == crossing_b.pd_code[2] and crossing_a.pd_code[2] == crossing_b.pd_code[1]:
        print 'the crossings form an arc -- check 1'
    elif crossing_a.pd_code[2] == crossing_b.pd_code[0] and crossing_a.pd_code[3] == crossing_b.pd_code[3]:
        print 'the crossings form an arc -- check 2'
    else:
        print 'the crossings do not form an arc'


def simplify_rm1_rm2_recursively(knot):
    """
    Simplify a knot by Reidemeister moves of types 1 & 2 until
    no more moves are possible.

    >>> simplify_rm1_rm2_recursively([[1,7,2,6],[2,9,3,10],[5,1,6,10],[7,5,8,4],[8,3,9,4]])
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



#Read in a CSV.
with open('knots.csv') as csvfile:
    fieldnames = ['name', 'pd_notation']
    knotreader = csv.DictReader(csvfile)

    for row in knotreader:
        # Evaluate strings containing Python lists.
        knot = Knot([Crossing(pd_code, 0) for pd_code in ast.literal_eval(row['pd_notation'])])

        print str(row['name'])
        print knot

        #simplify_rm1_rm2_recursively(knot)
        for current_item, next_item in izip(knot.crossings, numpy.roll(knot.crossings, -1)):
            compare_two_crossings(current_item, next_item)

# if __name__ == '__main__':
#     import doctest
#     doctest.testmod()
