#!/usr/bin/env python2.7

import itertools
from itertools import repeat
import logging
import numpy
import sys, os, csv, copy

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
    def __init__(self, crossings, name = None, bridges = None):
        self.name = name
        self.crossings = crossings # crossings is a list of Crossing objects
        self.free_crossings = crossings[:]
        self.bridges = []
        if bridges:
            for bridge in bridges:
                bridge_end = bridge[0]
                for free_crossing in self.free_crossings:
                    if (bridge_end in free_crossing.pd_code):
                        i = free_crossing.pd_code.index(bridge_end)
                        if ((i == 1) or (i == 3)):
                            self.designate_bridge(free_crossing)
                            break

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
        bridge_crossings = diff(self.crossings, self.free_crossings)
        bridge_ends = [x for bridge_ends in self.bridges for x in bridge_ends]
        all_bridge_segments = [crossing.pd_code[i] for crossing in bridge_crossings for i in [0, 2]]
        bridge_interior_segments = diff(all_bridge_segments, bridge_ends)

        for free_crossing in self.free_crossings:
            interior_match = list(set([free_crossing.pd_code[1], free_crossing.pd_code[3]]) & set(bridge_interior_segments))
            end_match = list(set(bridge_ends) & set(free_crossing.pd_code))
            if (interior_match or end_match):
                self.designate_bridge(free_crossing)
                return self

        logging.critical('We were unable to designate an additional bridge.')
        sys.exit('We were unable to designate an additional bridge for ' + self.name + '.')

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
        
    def drag_crossing_under_bridge(self, crossing_to_drag, adjacent_segment):
        def find_bridge_to_go_under(adjacent_segment):
            """
            Return the bridge crossing under which to drag a free crossing.

            Arguments:
            adjacent_segment -- (int) The PD code value of the segment to drag a crossing along.
            """
            for crossing in diff(self.crossings, self.free_crossings):
                if adjacent_segment in crossing.pd_code:
                    return crossing

        bridge_crossing = find_bridge_to_go_under(adjacent_segment)
        a, b, c, d = crossing_to_drag.pd_code
        e, f, g, h = bridge_crossing.pd_code
        new_max_pd_val = self.max_pd_code_value()+4
        bid = bridge_crossing.bridge
        y = bridge_crossing.overpass_traveled_from()
        adjacent_segment_index = crossing_to_drag.pd_code.index(adjacent_segment)

        logging.debug('We will drag ' + str(crossing_to_drag.pd_code) + ' under ' + str(bridge_crossing.pd_code))

        # Alter the PD codes of all crossings not invloved in the drag.
        a_y_sorted = sorted([a, y])
        for crossing in diff(self.crossings, [crossing_to_drag, bridge_crossing]):
            crossing.alter_for_drag(a_y_sorted)

        # Replace the crossing being dragged, (a,b,c,d).
        if d == e:
            i = sorted([a, y, b]).index(b)
            if a < y:
                m, n, r, s, t, u, v, w = a, a+1, a+2, a+3, a+1, a+2, alter_if_greater(b+1+2*i, new_max_pd_val, 0, new_max_pd_val), alter_if_greater(b+2+2*i, new_max_pd_val, 0, new_max_pd_val)
                if y == f:
                    logging.debug('Dragging case d=e, a<y, y==f')
                    y_vals_one = alter_y_values(y, [4,5], new_max_pd_val)
                    y_vals_two = alter_y_values(y, [3,2], new_max_pd_val)
                elif y == h:
                    logging.debug('Dragging case d=e, a<y, y==h')
                    y_vals_one = alter_y_values(y, [3,2], new_max_pd_val)
                    y_vals_two = alter_y_values(y, [4,5], new_max_pd_val)
            if a > y:
                m, n, r, s, t, u, v, w = a+2, a+3, a+4, alter_if_greater(a+5, new_max_pd_val, 0, new_max_pd_val), a+3, a+4, alter_if_greater(b+1+2*i, new_max_pd_val, 0, new_max_pd_val), alter_if_greater(b+2+2*i, new_max_pd_val, 0, new_max_pd_val)
                if y == f:
                    logging.debug('Dragging case d=e, a>y, y==f')
                    y_vals_one = alter_y_values(y, [2,3], new_max_pd_val)
                    y_vals_two = alter_y_values(y, [1,0], new_max_pd_val)
                elif y == h:
                    logging.debug('Dragging case d=e, a>y, y==h')
                    y_vals_one = alter_y_values(y, [1,0], new_max_pd_val)
                    y_vals_two = alter_y_values(y, [2,3], new_max_pd_val)
        elif b == e:
            i = sorted([a,y,d]).index(d)
            if a < y:
                m, n, r, s, t, u, v, w = a, a+1, a+2, a+3, a+1, a+2, alter_if_greater(d+2+2*i, new_max_pd_val, 0, new_max_pd_val), alter_if_greater(d+1+2*i, new_max_pd_val, 0, new_max_pd_val)
                if y == f:
                    logging.debug('Dragging case b=e, a<y, y==f')
                    y_vals_one = alter_y_values(y, [2,3], new_max_pd_val)
                    y_vals_two = alter_y_values(y, [5,4], new_max_pd_val)
                elif y == h:
                    logging.debug('Dragging case b=e, a<y, y==h')
                    y_vals_one = alter_y_values(y, [5,4], new_max_pd_val)
                    y_vals_two = alter_y_values(y, [2,3], new_max_pd_val)
            if a > y:
                m, n, r, s, t, u, v, w = a+2, a+3, a+4, alter_if_greater(a+5, new_max_pd_val, 0, new_max_pd_val), a+3, a+4, alter_if_greater(d+2+2*i, new_max_pd_val, 0, new_max_pd_val), alter_if_greater(d+1+2*i, new_max_pd_val, 0, new_max_pd_val)
                if y == f:
                    logging.debug('Dragging case b=e, a>y, y==f')
                    y_vals_one = alter_y_values(y, [0,1], new_max_pd_val)
                    y_vals_two = alter_y_values(y, [3,2], new_max_pd_val)
                elif y == h:
                    logging.debug('Dragging case b=e, a>y, y==h')
                    y_vals_one = alter_y_values(y, [3,2], new_max_pd_val)
                    y_vals_two = alter_y_values(y, [0,1], new_max_pd_val)
        elif d == g:
            i = sorted([a,y,e]).index(e)
            if a < y:
                m, n, r, s, t, u, v, w = a, a+1, a+2, a+3, a+1, a+2, alter_if_greater(e+1+2*i, new_max_pd_val, 0, new_max_pd_val), e+2*i
                if y == f:
                    logging.debug('Dragging case d=g, a<y, y==f')
                    y_vals_one = alter_y_values(y, [3,2], new_max_pd_val)
                    y_vals_two = alter_y_values(y, [4,5], new_max_pd_val)
                elif y == h:
                    logging.debug('Dragging case d=g, a<y, y==h')
                    y_vals_one = alter_y_values(y, [4,5], new_max_pd_val)
                    y_vals_two = alter_y_values(y, [3,2], new_max_pd_val)
            if a > y:
                m, n, r, s, t, u, v, w = a+2, a+3, a+4, alter_if_greater(a+5, new_max_pd_val, 0, new_max_pd_val), a+3, a+4, alter_if_greater(e+1+2*i, new_max_pd_val, 0, new_max_pd_val), e+2*i
                if y == f:
                    logging.debug('Dragging case d=g, a>y, y==f')
                    y_vals_one = alter_y_values(y, [1,0], new_max_pd_val)
                    y_vals_two = alter_y_values(y, [2,3], new_max_pd_val)
                elif y == h:
                    logging.debug('Dragging case d=g, a>y, y==h')
                    y_vals_one = alter_y_values(y, [2,3], new_max_pd_val)
                    y_vals_two = alter_y_values(y, [1,0], new_max_pd_val)
        elif b == g:
            i = sorted([a,y,e]).index(e)
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
        if b == e:
            m = alter_if_greater(d+2*i, new_max_pd_val, 0, new_max_pd_val)
            n = alter_if_greater(d+1+2*i, new_max_pd_val, 0, new_max_pd_val)
        if d == e:
            m = alter_if_greater(b+2*i, new_max_pd_val, 0, new_max_pd_val)
            n = alter_if_greater(b+1+2*i, new_max_pd_val, 0, new_max_pd_val)
        elif (d == g) or (b == g):
            m = alter_if_greater(e+1+2*i, new_max_pd_val, 0, new_max_pd_val)
            n = alter_if_greater(e+2+2*i, new_max_pd_val, 0, new_max_pd_val)
        addends = get_y_addends(a, h, y)
        bridge_crossing.pd_code = [m, y+addends[0], n, y+addends[1]]
        logging.debug('(e,f,g,h) becomes ' + str(bridge_crossing.pd_code))

        logging.debug('PD code of the knot after dragging is ' + str(self))

        # Alter PD code values of bridge ends.
        for i, bridge in enumerate(self.bridges):
            self.bridges[i] = map(alter_element_for_drag, bridge, repeat(a_y_sorted[0],2), repeat(a_y_sorted[1],2))

        # Check if the crossing we dragged is now covered by a bridge.
        for i, bridge in enumerate(self.bridges):
            for end in bridge:
                if (end == crossing_to_drag.pd_code[1]) or (end == crossing_to_drag.pd_code[3]):
                    self.extend_bridge(i)
                    logging.debug('Bridge end ' + str(end) + ' has been extended to cover the crossing we dragged')
        logging.debug('After dragging and altering, the bridges are ' + str(self.bridges))

        # Get the value of the next segment to drag along in case we continue with this crossing.
        next_segment = crossing_to_drag.pd_code[adjacent_segment_index]
        logging.debug('If we drag this crossing again, we should drag it along ' + str(next_segment))

        return crossing_to_drag, next_segment

    def drag_crossing_under_bridge_resursively(self, crossing_to_drag, adjacent_segment, drag_count):
        """
        Drag a crossing under multiple, consecutive bridges.

        Arguments:
        crossing_to_drag -- (obj) A Crossing to drag
        adjacent_segment -- (int) The PD code value of the adjacent segment to drag along
        drag_count -- (int) The number of bridges to drag the crossing underneath
        """
        while (drag_count > 0):
            crossing_to_drag, adjacent_segment = self.drag_crossing_under_bridge(crossing_to_drag, adjacent_segment)
            drag_count -= 1
            # Stop if the crossing being dragged has been assigned to a bridge.
            if crossing_to_drag.bridge:
                break;

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
        max_pd_code_value = self.max_pd_code_value()
        for bridge in self.bridges:
            for end in bridge:
                crossings_containing_end = []
                for crossing in diff(self.crossings, self.free_crossings):
                    if end in crossing.pd_code:
                        crossings_containing_end.append(crossing)
                if len(crossings_containing_end) == 2:
                    # end is a T stem.
                    logging.debug(str(end) + ' is a T stem')

                    # Get the value of the segment adjacent to end.
                    for end_crossing in crossings_containing_end:
                        i = end_crossing.pd_code.index(end)
                        if (i%2 == 0):
                            adjacent_segment = end_crossing.pd_code[(i+2)%4]
                            logging.debug('The segment adjacent to the T stem is ' + str(adjacent_segment))
                            # Determine the addend needed to calculate the next adjacent segment
                            # based on the direction we travel along the T stem.
                            if i == 0:
                                next_segment_addend = 1
                            else:
                                next_segment_addend = -1
                            logging.debug('The next_segment_addend is ' + str(next_segment_addend))
                            break;

                    drag_count = 0
                    continue_search = True
                    while continue_search:
                        reached_deadend = False

                        # Does adjacent_segment belong to a free crossing (deadend)?
                        for free_crossing in self.free_crossings:
                            if adjacent_segment in free_crossing.pd_code:
                                reached_deadend = True
                                break;

                        if reached_deadend:
                            if (free_crossing.pd_code.index(adjacent_segment)%2 == 1):
                                # The crossing is oriented such that we can drag it.
                                drag_count += 1
                                logging.debug('Crossing ' + str(free_crossing.pd_code) + ' can be dragged along ' + str(adjacent_segment))
                                return (free_crossing, adjacent_segment, drag_count)
                            else:
                                continue_search = False
                                logging.debug('We have completed our search of this stem')
                                break
                        else:
                            drag_count += 1
                            # Consider the next crossing along the T stem.
                            adjacent_segment = next_adjacent_segment(adjacent_segment, next_segment_addend, max_pd_code_value)
                            logging.debug('We need to consider the next crossing along the T stem containing ' + str(adjacent_segment))

        # If we check all of the bridge Ts and cannot find a crossing to drag,
        # return False to signify we need to identify a new bridge.
        logging.debug('There are no crossings to drag. We need to identify another bridge.')
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

    def list_bridge_ts(self, directory, depth):
        """
        Generate a list of bridge choices that form a "T".

        Arguments:
        directory -- (str) The base path to store all the output files.
        depth -- (int) The depth of the tree
        """
        if self.bridges == []:
            i = 1
            depth_suffix = '_' + str(depth)
            for a, b in itertools.combinations(self.free_crossings, 2):
                if list(set(a.pd_code).intersection(b.pd_code)):
                    name = self.name + '_tree_' + str(i) + depth_suffix
                    e,f,g,h = a.pd_code
                    p,q,r,s = b.pd_code
                    logging.debug('We found ' + name + ' at ' + str(a.pd_code) + ', ' + str(b.pd_code))
                    # Create the directory for this tree.
                    tree_directory = directory + '/tree_' + str(i)
                    if not os.path.exists(tree_directory):
                        os.makedirs(tree_directory)
                    # Create the file to store the tree root.
                    tree_file = tree_directory + '/tree_' + str(i) + depth_suffix + '.csv'
                    outfile = open(tree_file, "w")
                    outputwriter = csv.writer(outfile, delimiter=',')
                    outputwriter.writerow(['name','pd_notation','bridges'])
                    outputwriter.writerow([name,str(self),str([[f,h],[q,s]])])
                    i += 1
            outfile.close()
        else:
            # Check if a file for this knot & depth exists. If not, create the file.
            tree_prefix = directory.rsplit('/', 1)[1]
            depth_suffix = '_' + str(depth)
            file_name = tree_prefix + depth_suffix + '.csv'
            file_path = directory + '/' + file_name
            if not os.path.isfile(file_path):
                # Create the file we need with headers.
                with open(file_path, "w") as outfile:
                    outputwriter = csv.writer(outfile, delimiter=',')
                    outputwriter.writerow(['name','pd_notation','bridges'])
            # Find and store bridge Ts.
            i = 1
            bridge_crossings = diff(self.crossings, self.free_crossings)
            for a, b in itertools.product(bridge_crossings, self.free_crossings):
                knot_copy = copy.deepcopy(self)
                if list(set(a.pd_code).intersection(b.pd_code)):
                    knot_copy.designate_bridge(b)
                    knot_name_parts = self.name.rsplit('_', 1)
                    knot_copy_name = knot_name_parts[0] + '_' + str(i)
                    with open(file_path, "a") as outfile:
                        outputwriter = csv.writer(outfile, delimiter=',')
                        outputwriter.writerow([knot_copy_name,str(knot_copy),str(knot_copy.bridges)])
                    i += 1

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
        def alter_bridge_end_for_rm1(x, duplicate_value, max_value):
            if x > duplicate_value:
                x -= 2
                if x > max_value:
                    x = x%max_value
            elif x == duplicate_value:
                if duplicate_value == 1:
                    x = max_value
                elif duplicate_value == max_value+2:
                    x = 1
                else:
                    x -= 1
            return x

        crossings = self.crossings
        for index in sorted(twisted_crossings, reverse = True):
            duplicate_value = self.crossings[index].has_duplicate_value()
            original_max_value = len(self.crossings)*2
            self.delete_crossings([index])
            new_max_value = original_max_value-2

            if duplicate_value == original_max_value:
                extend_if_bridge_end = [1, duplicate_value + 1]
                # Adjust crossings.
                for crossing in self.crossings:
                    crossing.alter_elements_greater_than(new_max_value, -new_max_value, new_max_value)
            else:
                extend_if_bridge_end = [duplicate_value - 1, duplicate_value + 1]
                # Adjust crossings.
                for crossing in self.crossings:
                    crossing.alter_elements_greater_than(duplicate_value, -2, new_max_value)
            for i, bridge in enumerate(self.bridges):
                # Adjust bridges.
                self.bridges[i] = map(alter_bridge_end_for_rm1, bridge, repeat(duplicate_value, 2), repeat(new_max_value, 2))
                # Try to extend bridges.
                extend_bridge = any(x in bridge for x in extend_if_bridge_end)
                if extend_bridge:
                    bridge_index = self.bridges.index(bridge)
                    self.extend_bridge(bridge_index)

            logging.info('After simplifying the knot for RM1 at segment ' + str(duplicate_value) + ', the PD code is ' + str(self) + ' and the bridges are ' + str(self.bridges))
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
        maximum = len(self.crossings) * 2
        extend_if_bridge_end = []
        segments_to_eliminate.sort(reverse = True)

        logging.info('The segments ' + str(segments_to_eliminate[0][0]) + ' and ' + str(segments_to_eliminate[1][0]) + ' can be elimiated by RM2 moves.')

        for segment in segments_to_eliminate:
            value = segment[0]
            addend = segment[1]
            # Alter values of each crossing.
            for crossing in self.crossings:
                crossing.alter_elements_greater_than(value, addend)

            # Adjust bridges.
            for i, bridge in enumerate(self.bridges):
                self.bridges[i] = map(alter_if_greater, bridge, repeat(value, 2), repeat(addend, 2))

            # Alter values of remaining segments to eliminate.
            segments_to_eliminate = alter_segment_elements_greater_than(segments_to_eliminate, value, addend)

            # Remove segments as we finish with them.
            del(segments_to_eliminate[-1])

        # Mod final crossings based on maximum value allowed.
        for crossing in self.crossings:
            crossing.alter_elements_greater_than(maximum, 0, maximum)
        # Mod final bridge ends based on maximum value allowed.
        self.alter_bridge_segments_greater_than(maximum, 0, maximum)
                
        extend_if_bridge_end = [value - 1, value + 1]
        for bridge in self.bridges:
            extend_bridge = any(x in bridge for x in extend_if_bridge_end)
            if extend_bridge:
                bridge_index = self.bridges.index(bridge)
                self.extend_bridge(bridge_index)
        logging.info('After simplifying by RM2, the PD code is ' + str(self) + ' and the bridges are ' + str(self.bridges))

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
    x -- (int) The number to alter.
    value -- (int) The number to compare each element of the crossing with.
    addend -- (int) The number to add to crossing elements greater than value.
    maximum -- (int) The maximum allowed value of elements in the crossing.
    """
    if x > value:
        x += addend
        if x == 0:
            x = maximum
        if maximum and (x > maximum):
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

def create_knot_from_pd_code(pd_code, name = None, bridges = None):
    """
    Create a Knot object using a provided PD code.

    Arguments:
    pd_code -- (list) the PD notation of a knot expressed as a list of lists
    name -- (str) a string to identify the knot
    bridges -- (list) Each element is a list of PD code values for the ends of each bridge
    """
    return Knot([Crossing(crossing) for crossing in pd_code], name, bridges)

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

def next_adjacent_segment(current_segment, next_segment_addend, max_pd_code_value):
    """
    Given a direction of travel, return the PD code segment of the section adjacent to current_segment.

    Arguments:
    current_segment -- (int) The PD code value of the current segment
    next_segment_addend -- (int) 1 or -1, depending on the direction of travel
    max_pd_code_value -- (int) The maximum PD code value for the knot diagram.
    """
    next_segment = alter_if_greater(current_segment, 0, next_segment_addend, max_pd_code_value)
    if next_segment == 0:
        next_segment = max_pd_code_value
    return next_segment
