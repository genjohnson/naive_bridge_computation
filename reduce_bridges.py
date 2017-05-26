#!/usr/bin/env python2.7

import itertools
from json import JSONEncoder
import logging
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

    def alter_elements_greater_than(self, value, addend, maximum = None):
        """
        Change the value of all elements in a Crossing which are greater
        than the provided value.

        Arguments:
        value -- (int) The number to compare each element of the crossing with.
        addend -- (int) The number to add to crossing elements greater than value.
        maximum -- (int) The maximum allowed value of elements in the crossing.
        """
        self.pd_code = [alter_if_greater(x, value, addend, maximum) for x in self.pd_code]
        return self

    def alter_for_drag(self, ordered_segments):
        self.pd_code = [alter_element_for_drag(x, ordered_segments[0], ordered_segments[1]) for x in self.pd_code]
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

    def overpass_traveled_from(self):
        """
        Find the value of the overcross segment of a crossing we travel from toward the other.
        """
        e,f,g,h = self.pd_code
        if abs(f - h) == 1:
            return min(f, h)
        else:
            return max(f, h)

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

    def alter_bridge_segments_greater_than(self, value, addend, maximum = None):
        """
        Change the value of the bridge end segments if they are greater
        than the provided value.

        Arguments:
        value -- (int) The number to compare each segment with.
        addend -- (int) The number to add to the segments greater than value.
        maximum -- (int) The maximum allowed value of segments in the bridge.
        """
        for bridge in self.bridges:
            bridge_index = self.bridges.index(bridge)
            for x in bridge:
                x_index = bridge.index(x)
                self.bridges[bridge_index][x_index] = alter_if_greater(x, value, addend, maximum)
        return self

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

    def designate_additional_bridge(self):
        """
        Choose a crossing to designate as a bridge based on existing bridges.
        """
        for bridge in self.bridges:
            # Sort the bridge ends to first follow the orientation of the knot
            # when searching for the next available crossing.
            for x in sorted(bridge, reverse = True):
                for free_crossing in self.free_crossings:
                    if x == free_crossing.pd_code[0]:
                        self.designate_bridge(free_crossing)
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
        logging.debug('Crossing ' + str(crossing.pd_code) + ' has been designated as a bridge with index ' + str(crossing.bridge))
        self.extend_bridge(crossing.bridge)
        
    def drag_crossing_under_bridge(self, crossing_to_drag, bridge_crossing):
        a, b, c, d = crossing_to_drag.pd_code
        e, f, g, h = bridge_crossing.pd_code
        new_max_pd_val = self.max_pd_code_value()+4
        bid = bridge_crossing.bridge
        y = bridge_crossing.overpass_traveled_from()

        # Following the orientation of the knot, find when we traverse e.
        i = sorted([a, e, y]).index(e)

        # Alter the PD codes of all crossings not invloved in the drag.
        a_y_sorted = sorted([a, y])
        for crossing in diff(self.crossings, [crossing_to_drag, bridge_crossing]):
            crossing.alter_for_drag(a_y_sorted)

        # Replace the crossing being dragged, (a,b,c,d).
        if d == e:
            if a < y:
                m, n, r, s, t, u, v, w = a, a+1, a+2, a+3, a+1, a+2, e+2*i, alter_if_greater(e+1+2*i, new_max_pd_val, 0, new_max_pd_val)
                if y == f:
                    logging.debug('Dragging case d=e, a<y, y==f')
                    y_vals_one = alter_y_values(y, [4,5], new_max_pd_val)
                    y_vals_two = alter_y_values(y, [3,2], new_max_pd_val)
                elif y == h:
                    logging.debug('Dragging case d=e, a<y, y==h')
                    y_vals_one = alter_y_values(y, [3,2], new_max_pd_val)
                    y_vals_two = alter_y_values(y, [4,5], new_max_pd_val)
            if a > y:
                m, n, r, s, t, u, v, w = a+2, a+3, a+4, alter_if_greater(a+5, new_max_pd_val, 0, new_max_pd_val), a+3, a+4, e+2*i, alter_if_greater(e+1+2*i, new_max_pd_val, 0, new_max_pd_val)
                if y == f:
                    logging.debug('Dragging case d=e, a>y, y==f')
                    y_vals_one = alter_y_values(y, [2,3], new_max_pd_val)
                    y_vals_two = alter_y_values(y, [1,0], new_max_pd_val)
                elif y == h:
                    logging.debug('Dragging case d=e, a>y, y==h')
                    y_vals_one = alter_y_values(y, [1,0], new_max_pd_val)
                    y_vals_two = alter_y_values(y, [2,3], new_max_pd_val)
        elif b == e:
            if a < y:
                m, n, r, s, t, u, v, w = a, a+1, a+2, a+3, a+1, a+2, alter_if_greater(e+1+2*i, new_max_pd_val, 0, new_max_pd_val), e+2*i
                if y == f:
                    logging.debug('Dragging case b=e, a<y, y==f')
                    y_vals_one = alter_y_values(y, [2,3], new_max_pd_val)
                    y_vals_two = alter_y_values(y, [5,4], new_max_pd_val)
                elif y == h:
                    logging.debug('Dragging case b=e, a<y, y==h')
                    y_vals_one = alter_y_values(y, [5,4], new_max_pd_val)
                    y_vals_two = alter_y_values(y, [2,3], new_max_pd_val)
            if a > y:
                m, n, r, s, t, u, v, w = a+2, a+3, a+4, alter_if_greater(a+5, new_max_pd_val, 0, new_max_pd_val), a+3, a+4, alter_if_greater(e+1+2*i, new_max_pd_val, 0, new_max_pd_val), e+2*i
                if y == f:
                    logging.debug('Dragging case b=e, a>y, y==f')
                    y_vals_one = alter_y_values(y, [0,1], new_max_pd_val)
                    y_vals_two = alter_y_values(y, [3,2], new_max_pd_val)
                elif y == h:
                    logging.debug('Dragging case b=e, a>y, y==h')
                    y_vals_one = alter_y_values(y, [3,2], new_max_pd_val)
                    y_vals_two = alter_y_values(y, [0,1], new_max_pd_val)
        elif d == g:
            if a < y:
                m, n, r, s, t, u, v, w = a, a+1, a+2, a+3, a+1, a+2, e+1, e
                if y == f:
                    logging.debug('Dragging case d=g, a<y, y==f')
                    y_vals_one = alter_y_values(y, [3,2], new_max_pd_val)
                    y_vals_two = alter_y_values(y, [4,5], new_max_pd_val)
                elif y == h:
                    logging.debug('Dragging case d=g, a<y, y==h')
                    y_vals_one = alter_y_values(y, [4,5], new_max_pd_val)
                    y_vals_two = alter_y_values(y, [3,2], new_max_pd_val)
            if a > y:
                m, n, r, s, t, u, v, w = a+2, a+3, a+4, alter_if_greater(a+5, new_max_pd_val, 0, new_max_pd_val), a+3, a+4, e+1, e+2
                if y == f:
                    logging.debug('Dragging case d=g, a>y, y==f')
                    y_vals_one = alter_y_values(y, [1,0], new_max_pd_val)
                    y_vals_two = alter_y_values(y, [2,3], new_max_pd_val)
                elif y == h:
                    logging.debug('Dragging case d=g, a>y, y==h')
                    y_vals_one = alter_y_values(y, [2,3], new_max_pd_val)
                    y_vals_two = alter_y_values(y, [1,0], new_max_pd_val)
        elif b == g:
            if a < y:
                m, n, r, s, t, u, v, w = a, a+1, a+2, a+3, a+1, a+2, e+2*i, alter_if_greater(e+1+2*i, new_max_pd_val, 0, new_max_pd_val)
                if y == f:
                    logging.debug('Dragging case b=g, a<y, y==f')
                    y_vals_one = alter_y_values(y, [5,4], new_max_pd_val)
                    y_vals_two = alter_y_values(y, [2,3], new_max_pd_val)
                elif y == h:
                    logging.debug('Dragging case b=g, a<y, y==h')
                    y_vals_one = alter_y_values(y, [2,3], new_max_pd_val)
                    y_vals_two = alter_y_values(y, [5,4], new_max_pd_val)
            if a > y:
                m, n, r, s, t, u, v, w = a+2, a+3, a+4, alter_if_greater(a+5, new_max_pd_val, 0, new_max_pd_val), a+3, a+4, e+2*i, alter_if_greater(e+1+2*i, new_max_pd_val, 0, new_max_pd_val)
                if y == f:
                    logging.debug('Dragging case b=g, a>y, y==f')
                    y_vals_one = alter_y_values(y, [3,2], new_max_pd_val)
                    y_vals_two = alter_y_values(y, [0,1], new_max_pd_val)
                elif y == h:
                    logging.debug('Dragging case b=g, a>y, y==h')
                    y_vals_one = alter_y_values(y, [0,1], new_max_pd_val)
                    y_vals_two = alter_y_values(y, [3,2], new_max_pd_val)

        crossing_one = Crossing([m, y_vals_one[0], n, y_vals_one[1]], bid)
        crossing_two = Crossing([r, y_vals_two[0], s, y_vals_two[1]], bid)
        crossing_to_drag.pd_code = [t, v, u, w]
        index = self.crossings.index(crossing_to_drag)
        self.crossings[index:index+1] = crossing_one, crossing_to_drag, crossing_two
        logging.debug('(a,b,c,d) becomes ' + str(crossing_one.pd_code) + str(crossing_to_drag.pd_code) + str(crossing_two.pd_code))

        # Alter the PD code of the bridge crossing, (e,f,g,h).
        if (d == e) or (b == e):
            m = alter_if_greater(e+2*i, new_max_pd_val, 0, new_max_pd_val)
            n = alter_if_greater(e+1+2*i, new_max_pd_val, 0, new_max_pd_val)
        elif (d == g) or (b == g):
            m = alter_if_greater(e+1+2*i, new_max_pd_val, 0, new_max_pd_val)
            n = alter_if_greater(e+2+2*i, new_max_pd_val, 0, new_max_pd_val)
        addends = get_y_addends(a, h, y)
        bridge_crossing.pd_code = [m, y+addends[0], n, y+addends[1]]
        logging.debug('(e,f,g,h) becomes ' + str(bridge_crossing.pd_code))

        logging.debug('PD code of the knot after dragging is ' + str(self))

        # Alter PD code values of bridge ends.
        logging.debug('Before dragging, the bridges are ' + str(self.bridges))
        bridge_to_extend = None
        for i, bridge in enumerate(self.bridges):
            for j, end in enumerate(bridge):
                end = alter_element_for_drag(end, a_y_sorted[0], a_y_sorted[1])
                self.bridges[i][j] = end
                # Check if the crossing we dragged is now covered by a bridge.
                if (end == crossing_to_drag.pd_code[1]) or (end == crossing_to_drag.pd_code[3]):
                    bridge_to_extend = i
                    logging.debug('Bridge end ' + str(end) + ' can be extended to cover the crossing we dragged')
        # Expand the bridge covering the crossing that was dragged.
        if bridge_to_extend != None:
            self.extend_bridge(bridge_to_extend)
        logging.debug('After altering, the bridges are ' + str(self.bridges))

    def extend_bridge(self, bridge_index):
        """
        Extend both ends of a bridge until it deadends.

        Arguments:
        bridge_index -- (int) the index of the bridge to extend
        """
        bridge = self.bridges[bridge_index]
        logging.debug('We will try to extend the bridge ' + str(bridge))
        for x in bridge:
            index = bridge.index(x)
            x_is_deadend = False
            while (x_is_deadend == False):
                result = filter(lambda free_crossing: x in free_crossing.pd_code, self.free_crossings)
                if result:
                    crossing = result.pop()
                    if x == crossing.pd_code[1]:
                        logging.debug('Bridge end ' + str(x) + ' can be extended to ' + str(crossing.pd_code[3]))
                        bridge[index] = crossing.pd_code[3]
                        x = crossing.pd_code[3]
                        self.free_crossings.remove(crossing)
                        crossing.bridge = bridge_index
                    elif x == crossing.pd_code[3]:
                        logging.debug('Bridge end ' + str(x) + ' can be extended to ' + str(crossing.pd_code[1]))
                        bridge[index] = crossing.pd_code[1]
                        x = crossing.pd_code[1]
                        self.free_crossings.remove(crossing)
                        crossing.bridge = bridge_index
                    else:
                        logging.debug('Bridge end ' + str(x) + ' is a dead-end and cannot be extended')
                        x_is_deadend = True
                else:
                    break;

    def find_crossing_to_drag(self):
        for crossing in self.free_crossings:
            args = crossing_deadends_at_bridge(self, crossing)
            if (args) and (deadend_adjacent_to_bridge(self, *args)):
                return (crossing, args[0])
        return False

    def has_rm1(self):
        """
        Inspect a knot for crossings that can be eliminated
        by Reidemeister moves of type 1.
        """
        twisted_crossings = []
        for index, crossing in enumerate(self.crossings):
            if crossing.has_duplicate_value():
                twisted_crossings.append(index)
                logging.debug('The knot can be simplified by RM1 at crossing ' + str(crossing.pd_code))
                return twisted_crossings
        return False

    def has_rm2(self):
        """
        Inspect a knot for crossings that can be eliminated
        by Reidemeister moves of type 2.

        Return the crossings which form an arc and
        the PD code value of the segments which will be eliminated when the
        knot is simplified.
        """
        def compare_pd_codes_for_rm2(indices_to_compare, current_crossing, next_crossing):
            output = False
            for comparision in indices_to_compare:
                current_comparision = [current_crossing.pd_code[comparision[0][0]], current_crossing.pd_code[comparision[0][1]]]
                next_comparison = [next_crossing.pd_code[comparision[1][0]], next_crossing.pd_code[comparision[1][1]]]
                if current_comparision == next_comparison: # True if a RM2 move is possible.
                    pd_code_segments_to_eliminate = []
                    for segment_to_eliminate in current_comparision:
                        if segment_to_eliminate == 1:
                            pd_code_segments_to_eliminate.append([segment_to_eliminate, -1])
                        else:
                            pd_code_segments_to_eliminate.append([segment_to_eliminate, -2])
                    output = ([index, next_index], pd_code_segments_to_eliminate)
                    break
            return output

        num_crossings = len(self.crossings)
        has_rm2 = False
        for index, current_crossing in enumerate(self.crossings):
            if has_rm2 == False:
                next_index = (index+1)%num_crossings
                next_crossing = self.crossings[next_index]
                difference = max(current_crossing.pd_code[0], next_crossing.pd_code[0]) - min(current_crossing.pd_code[0], next_crossing.pd_code[0])
                if (difference == 1):
                    indices_to_compare = [[[2,3],[0,3]],[[1,2],[1,0]]]
                    has_rm2 = compare_pd_codes_for_rm2(indices_to_compare, current_crossing, next_crossing)
                elif (difference == num_crossings-1):
                    indices_to_compare = [[[0,3],[2,3]],[[0,1],[2,1]]]
                    has_rm2 = compare_pd_codes_for_rm2(indices_to_compare, current_crossing, next_crossing)
            else:
                break
        return has_rm2

    def json(self):
        return dict(name = self.name, crossings = self.crossings, naive_bridges = len(self.bridges))

    def max_pd_code_value(self):
        """
        Return the maximum value possible in the PD code.
        """
        return len(self.crossings)*2

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
            self.delete_crossings([index])
            max_value = len(self.crossings)*2
            # Adjust crossings.
            addend = 0
            if duplicate_value <= max_value:
                addend = -2
            logging.debug('Add ' + str(addend) + ' to all crossing elements greater than ' + str(duplicate_value) + ' and mod by ' + str(max_value))
            for crossing in self.crossings:
                crossing.alter_elements_greater_than(duplicate_value, addend, max_value)
            # Adjust bridges.
            self.alter_bridge_segments_greater_than(duplicate_value, -2, max_value)
            extend_if_bridge_end = [duplicate_value - 1, duplicate_value + 1]
            for bridge in self.bridges:
                extend_bridge = any(x in bridge for x in extend_if_bridge_end)
                if extend_bridge:
                    bridge_index = self.bridges.index(bridge)
                    self.extend_bridge(bridge_index)
            logging.info('After simplifying the knot for RM1 at segment ' + str(duplicate_value) + ', the PD code is ' + str(self))
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
        self.delete_crossings(crossing_indices)
        extend_if_bridge_end = []
        segments_to_eliminate.sort(reverse = True)

        for segment in segments_to_eliminate:
            value = segment[0]
            addend = segment[1]
            # Alter values of each crossing.
            for crossing in self.crossings:
                crossing.alter_elements_greater_than(value, addend)
            # Alter values of remaining segments to eliminate.
            segments_to_eliminate = alter_segment_elements_greater_than(segments_to_eliminate, value, addend)
            # Remove segments as we finish with them.
            del(segments_to_eliminate[-1])

        # Mod final crossings based on maximum value allowed.
        maximum = len(self.crossings) * 2
        for crossing in self.crossings:
            crossing.alter_elements_greater_than(maximum, 0, maximum)

        # Adjust bridges.
        self.alter_bridge_segments_greater_than(value, addend, maximum)
        extend_if_bridge_end = [value - 1, value + 1]
        for bridge in self.bridges:
            extend_bridge = any(x in bridge for x in extend_if_bridge_end)
            if extend_bridge:
                bridge_index = self.bridges.index(bridge)
                self.extend_bridge(bridge_index)
        logging.info('After simplifying RM2 of arcs ' + str(segments_to_eliminate) + ', the PD code is ' + str(self))

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
                logging.info('No more moves of type RM1 or RM2 are possible.')
                break;
        return self

class ComplexEncoder(JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'json'):
            return obj.json()
        else:
            return json.JSONEncoder.default(self, obj)

def alter_element_for_drag(x, first, second):
    """
    A helper function for the drag the underpass move to adjust PD code values
    of crossings not directly invloved in the move.

    Arguments:
    x -- (int) The value to alter.
    first -- (int) The PD code value of the first segment we travel into.
    second -- (int) The PD code value of the second segment we travel into.
    """
    if x <= first:
        return x
    if first < x <= second:
        return x+2
    if x > second:
        return x+4

def alter_if_greater(x, value, addend, maximum = None):
    """
    Arguments:
    value -- (int) The number to compare each element of the crossing with.
    addend -- (int) The number to add to crossing elements greater than value.
    maximum -- (int) The maximum allowed value of elements in the crossing.
    """
    if x > value:
        x += addend
        if maximum and x > maximum:
            x = x%maximum
    return x

def alter_segment_elements_greater_than(segments, value, addend):
    """
    Arguments:
    segments -- (list) A list of lists of integers to alter.
    value -- (int) The number to compare each element of the crossing with.
    addend -- (int) The number to add to crossing elements greater than value.
    """
    altered_segments = []
    for pair in segments:
        altered_segments.append([alter_if_greater(x, value, addend) for x in pair])
    return altered_segments

def alter_y_values(y, addends, maximum):
    """
    A helper function for the drag the underpass move.

    Arguments:
    y -- (int) The PD code value of f or h, whichever we travel from toward the other.
    addends -- (list) Integer values to add to y.
    maximum -- (int) The maximum PD code value in the knot after dragging a crossing.
    """
    y_vals = [alter_if_greater(y+addend, maximum, 0, maximum) for addend in addends]
    return y_vals

def create_knot_from_pd_code(pd_code, name = None):
    """
    Create a Knot object using a provided PD code.

    Arguments:
    pd_code -- (list) the PD notation of a knot expressed as a list of lists
    """
    return Knot([Crossing(crossing) for crossing in pd_code], name)

def crossing_deadends_at_bridge(knot, crossing):
    """
    Determine if a crossing ends at a bridge overpass.

    Arguments:
    knot -- (object) a Knot
    crossing -- (object) a Crossing
    """
    bridge_crossings = diff(knot.crossings, knot.free_crossings)
    crossing_overpass = [crossing.pd_code[1], crossing.pd_code[3]]

    for i, x in enumerate(crossing_overpass):
        for bridge_crossing in bridge_crossings:
            for index in [0, 2]:
                if x == bridge_crossing.pd_code[index]:
                    logging.info('Crossing ' + str(crossing.pd_code) + ' dead-ends at a bridge')
                    return (bridge_crossing, x)
    return False

def deadend_adjacent_to_bridge(knot, crossing, deadend):
    """
    Determine if a crossing end is adjacent to the end of a bridge.

    Arguments:
    knot -- (object) a Knot
    crossing -- (object) a Crossing that is covered by a bridge
    deadend -- (int) the PD code value of the crossing segment to evaluate
    """
    i = crossing.pd_code.index(deadend)
    segment_adjacent_to_deadend = crossing.pd_code[(i+2)%4]
    for bridge in knot.bridges:
        if segment_adjacent_to_deadend in bridge:
            logging.debug('Segment ' + str(deadend) + ' is adjacent to bridge end ' +str(segment_adjacent_to_deadend))
            return segment_adjacent_to_deadend
    logging.debug('Segment ' + str(deadend) + ' is not adjacent to a bridge end')
    return False

def diff(first, second):
    """
    Compute the difference of two lists.

    Arguments:
    first -- (list) The list to prune
    second -- (list) The elements to remove from "first" (if they exist)
    """
    second = set(second)
    return [item for item in first if item not in second]

def get_y_addends(a, h, y):
    """
    Get the addends for y to alter the bridge tuple for a drag.

    Arguments:
    a -- (int) PD code of the 1st element in the tuple being dragged.
    h -- (int) PD code of the 4th element in the bridge tuple.
    y -- (int) PD code of the 2nd or 4th element in the bridge tuple that is traveled from toward the other.
    """
    if a < y:
        addends = [3,4]
    elif a > y:
        addends = [1,2]
    addends.sort(reverse = bool(y == h))
    return addends
