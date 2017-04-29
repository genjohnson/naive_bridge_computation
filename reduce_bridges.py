#!/usr/bin/env python2.7

import itertools
from json import JSONEncoder
import numpy

class Crossing:
    def __init__(self, pd_code, bridge = None):
        self.pd_code = pd_code
        self.bridge = bridge

    def __eq__(self, other):
        return self.pd_code == other.pd_code and self.bridge == other.bridge

    def __hash__(self):
        return hash(tuple(self.pd_code))

    def __str__(self):
        return str([self.pd_code, self.bridge])

    def alter_elements_greater_than(self, value, addend, maximum):
        """
        Change the value of all elements in a Crossing which are greater
        than the provided value.

        Arguments:
        value -- (int) The number to compare each element of the crossing with.
        addend -- (int) The number to add to crossing elements greater than value.
        maximum -- (int) The maximum allowed value of elements in the crossing.
        """
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

    def json(self):
        return self.__dict__

class Knot:
    def __init__(self, crossings, name = None):
        self.name = name
        self.crossings = crossings # crossings is a list of Crossing objects
        self.bridges = []
        self.free_crossings = crossings[:]

    def __eq__(self, other):
        return self.crossings == other.crossings

    def __str__(self):
        return str([crossing.pd_code for crossing in self.crossings])

    def alter_bridge_segments_greater_than(self, value, addend, maximum):
        """
        Change the value of the bridge end segments if they are greater
        than the provided value.

        Arguments:
        value -- (int) The number to compare each segment with.
        addend -- (int) The number to add to the segments greater than value.
        maximum -- (int) The maximum allowed value of segments in the bridge.
        """
        for bridge in self.bridges:
            for x in bridge:
                alter_and_mod(x, value, addend, maximum)

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

    def json(self):
        return dict(name = self.name, crossings = self.crossings)

    def delete_crossings(self, indices):
        """
        Delete crossings from a knot.
        This removes objects from both knot.crossings and knot.free_crossings.

        Arguments:
        indices -- (list) the indices of the crossings to delete
        """
        # Delete crossings from last to first to avoid changing
        # the index of crossings not yet processed.
        indices.sort(reverse = True)
        for index in indices:
            del self.crossings[index]
        self.free_crossings = list(set(self.crossings).intersection(self.free_crossings))
        return self

    def designate_bridge(self, crossing):
        """
        Identify a crossing as a bridge and extend until it deadends.

        Arguments:
        crossing -- (obj) a crossing
        """
        self.bridges.append([crossing.pd_code[1], crossing.pd_code[3]])
        self.free_crossings.remove(crossing)
        crossing.bridge = len(self.bridges) - 1
        self.extend_bridge(crossing.bridge)

    def extend_bridge(self, bridge_index):
        """
        Extend both ends of a bridge until it deadends.

        Arguments:
        bridge_index -- (int) the index of the bridge to extend
        """
        bridge = self.bridges[bridge_index]
        for x in bridge:
            index = bridge.index(x)
            x_is_deadend = False
            while (x_is_deadend == False):
                result = filter(lambda free_crossing: x in free_crossing.pd_code, self.free_crossings)
                if result:
                    crossing = result.pop()
                    if x == crossing.pd_code[1]:
                        bridge[index] = crossing.pd_code[3]
                        x = crossing.pd_code[3]
                        self.free_crossings.remove(crossing)
                        crossing.bridge = bridge_index
                    elif x == crossing.pd_code[3]:
                        bridge[index] = crossing.pd_code[1]
                        x = crossing.pd_code[1]
                        self.free_crossings.remove(crossing)
                        crossing.bridge = bridge_index
                    else:
                        x_is_deadend = True
                else:
                    break;

    def num_crossings(self):
        """
        Return the number of crossings in the knot.
        """
        return len(self.crossings)

    def simplify_rm1(self, twisted_crossings):
        """
        Simplify one level of a knot by Reidemeister moves of type 1.

        Arguments:
        twisted_crossings -- (list) the indices of crossings to eliminate
        """
        crossings = self.crossings
        for index in sorted(twisted_crossings, reverse = True):
            duplicate_value = self.crossings[index].has_duplicate_value()
            max_value = len(self.crossings)*2
            # Adjust crossings.
            for crossing in self.crossings:
                crossing.alter_elements_greater_than(duplicate_value, -2, max_value)
            self.delete_crossings([index])
            # Adjust bridges.
            self.alter_bridge_segments_greater_than(duplicate_value, -2, max_value)
            extend_if_bridge_end = [duplicate_value - 1, duplicate_value + 1]
            for bridge in self.bridges:
                extend_bridge = any(x in bridge for x in extend_if_bridge_end)
                if extend_bridge:
                    bridge_index = self.bridges.index(bridge)
                    self.extend_bridge(bridge_index)      
        return self

    def simplify_rm1_recursively(self):
        """
        Simplify a knot by Reidemeister moves of type 1 until
        no more moves are possible.
        """
        while True:
            moves_possible = self.has_rm1()
            if moves_possible:
                print 'the knot has a twsit'
                print str(moves_possible)
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
        self.delete_crossings(crossing_indices)
        if 1 in segments_to_eliminate:
            for crossing in self.crossings:
                crossing.alter_elements_greater_than(max(segments_to_eliminate), -2, (len(self.crossings)+2)*2)
                crossing.alter_elements_greater_than(min(segments_to_eliminate), -1, len(self.crossings)*2)
            self.alter_bridge_segments_greater_than(max(segments_to_eliminate), -2, (len(self.crossings)+2)*2)
            self.alter_bridge_segments_greater_than(min(segments_to_eliminate), -1, len(self.crossings)*2)
        else:
            for crossing in self.crossings:
                crossing.alter_elements_greater_than(max(segments_to_eliminate), -2, (len(self.crossings)+2)*2)
                crossing.alter_elements_greater_than(min(segments_to_eliminate), -2, len(self.crossings)*2)
            self.alter_bridge_segments_greater_than(max(segments_to_eliminate), -2, (len(self.crossings)+2)*2)
            self.alter_bridge_segments_greater_than(min(segments_to_eliminate), -2, len(self.crossings)*2)
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

class ComplexEncoder(JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'json'):
            return obj.json()
        else:
            return json.JSONEncoder.default(self, obj)

def alter_and_mod(x, value, addend, maximum):
    """
    Arguments:
    value -- (int) The number to compare each element of the crossing with.
    addend -- (int) The number to add to crossing elements greater than value.
    maximum -- (int) The maximum allowed value of elements in the crossing.
    """
    if x > value:
        if x <= maximum-addend:
            x += addend
        else:
            x = (x+addend)%maximum
    return x

def create_knot_from_pd_code(pd_code, name = None):
    """
    Create a Knot object using a provided PD code.

    Arguments:
    pd_code -- (list) the PD notation of a knot expressed as a list of lists
    """
    return Knot([Crossing(crossing) for crossing in pd_code], name)
