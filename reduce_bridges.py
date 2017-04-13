#!/usr/bin/env python2.7

import itertools
from itertools import izip, islice
import numpy

class Crossing:
    def __init__(self, pd_code, bridge):
        self.pd_code = pd_code
        self.bridge = bridge

    def __eq__(self, other):
        return self.pd_code == other.pd_code and self.bridge == other.bridge

    def alter_elements_greater_than(self, value, addend, maximum):
        """
        Change the value of all elements in a Crossing which are greater
        than the provided value.

        Arguments:
        value -- (int) The number to compare each element of the crossing with.
        addend -- (int) The number to add to crossing elements greater than value.
        maximum -- (int) The maximum allowed value of elements in the crossing.
        """
        def alter_and_mod(x, value, addend, maximum):
            if x > value:
                if x <= maximum-addend:
                    print 'we perform ' + str(x) + '+' + str(addend)
                    x += addend
                else:
                    print 'we perform ' + str(x) + '%' + str(maximum)
                    x = (x+addend)%maximum
            return x

        self.pd_code = [alter_and_mod(x, value, addend, maximum) for x in self.pd_code]
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

    def has_rm2(self):
        """
        Inspect a knot for crossings that can be eliminated
        by Reidemeister moves of type 2.

        Return the crossings which form an arc and 
        the PD code value of the segments which will be eliminated when the
        knot is simplified.
        """
        crossings_formings_arcs = []
        pd_code_segments_to_eliminate = []
        rolled_crossings = numpy.roll(self.crossings, -1)
        num_crossings = len(self.crossings)
        for index, current_crossing in enumerate(self.crossings):
            next_index = (index+1)%num_crossings
            next_crossing = self.crossings[next_index]
            # arc type 1
            if current_crossing.pd_code[1] == next_crossing.pd_code[2] and current_crossing.pd_code[2] == next_crossing.pd_code[1]:
                crossings_formings_arcs.extend([index, next_index])
                pd_code_segments_to_eliminate.extend([current_crossing.pd_code[1], current_crossing.pd_code[2]])
            # arc type 2
            elif current_crossing.pd_code[2] == next_crossing.pd_code[0] and current_crossing.pd_code[3] == next_crossing.pd_code[3]:
                crossings_formings_arcs.extend([index, next_index])
                pd_code_segments_to_eliminate.extend([current_crossing.pd_code[2], current_crossing.pd_code[3]])
        if crossings_formings_arcs:
            return (crossings_formings_arcs, pd_code_segments_to_eliminate)
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
                crossing.alter_elements_greater_than(duplicate_value, -2, len(self.crossings)*2)
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

    def simplify_rm2(self, crossing_indices, segments_to_eliminate):
        """Simplify a knot by one Reidemeister move of type 2.

        Arguments:
        crossing_indices -- (list) the indices of crossings to remove
        segments_to_eliminate -- (list) integer values corresponding to the segments which are simplified
        """
        self.remove_crossings(crossing_indices)

        if 1 in segments_to_eliminate:
            for crossing in self.crossings:
                crossing.alter_elements_greater_than(max(segments_to_eliminate), -2, (len(self.crossings)+2)*2)
                crossing.alter_elements_greater_than(min(segments_to_eliminate), -1, len(self.crossings)*2)
        else:
            for crossing in self.crossings:
                crossing.alter_elements_greater_than(max(segments_to_eliminate), -2, (len(self.crossings)+2)*2)
                crossing.alter_elements_greater_than(min(segments_to_eliminate), -2, len(self.crossings)*2)
        return self

    def simplify_rm2_recursively(self):
        """Simplify a knot by Reidemeister moves of type 2 until
        no more moves are possible.
        """
        while True:
            moves_possible = self.has_rm2()
            if moves_possible:
                self.simplify_rm2(moves_possible[0], moves_possible[1])
            if not moves_possible:
                break;
        return self

    def simplify_rm1_rm2_recursively(self):
        """
        Simplify a knot by Reidemeister moves of types 1 & 2 until
        no more moves are possible.
        """
        while True:
            if self.has_rm1():
                self.simplify_rm1_recursively()
            if self.has_rm2():
                self.simplify_rm2_recursively()
            if not self.has_rm1() and not self.has_rm2():
                break;
        return self
