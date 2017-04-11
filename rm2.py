#!/usr/bin/env python2.7

import ast
import csv

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
