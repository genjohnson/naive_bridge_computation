#!/usr/bin/env python2.7

import ast
import csv
from common import *

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

def simplify_rm2(overlayed_crossings, removed_segments, knot):
    """Simplify a knot by one Reidemeister move of type 2.

    >>> simplify_rm2([3,4],[8,4],[[1,7,2,6],[2,9,3,10],[5,1,6,10],[7,5,8,4],[8,3,9,4]])
    [[1, 5, 2, 4], [2, 5, 3, 6], [3, 1, 4, 6]]

    Arguments:
    overlayed_crossings -- a list of indices of crossings to remove
    removed_segments -- the segments to remove as part of the move
    knot -- the PD notation of a knot
    """
    remove_tuples(overlayed_crossings, knot)
    alter_elements_greater_than(knot, min(removed_segments), -2)
    alter_elements_greater_than(knot, max(removed_segments)-2, -2)
    return knot

def simplify_rm2_recursive(knot):
    """Simplify a knot by Reidemeister moves of type 2 until
    no more moves are possible.

    >>> simplify_rm2_recursive([[1,7,2,6],[2,9,3,10],[5,1,6,10],[7,5,8,4],[8,3,9,4]])
    [[1, 3, 2, 2]]

    Arguments:
    knot -- the PD notation of a knot
    """
    while True:
        moves_possible = check_rm2(knot)
        if moves_possible:
            simplify_rm2(moves_possible[0], moves_possible[1], knot)
        if not moves_possible:
            break;
    return knot

# if __name__ == '__main__':
#     import doctest
#     doctest.testmod()
