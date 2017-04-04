# #!/usr/bin/env python2.7

import ast
import csv

def simplify_rm1(twisted_crossings, knot):
    """Simplify one level of a knot by Reidemeister moves of type 1.

    Arguments:
    twisted_crossings -- (list) the indices of crossings to eliminate
    knot -- (object) a knot
    """
    for index in twisted_crossings:
        duplicate_value = has_duplicate_value(knot.crossings[index].pd_code)
        alter_elements_greater_than(knot, duplicate_value, -2)

    remove_tuples(twisted_crossings, knot)
    return knot

def simplify_rm1_recursive(knot):
    """Simplify a knot by Reidemeister moves of type 1 until
    no more moves are possible.

    >>> simplify_rm1_recursive([[1, 5, 2, 4], [3, 3, 4, 2], [6, 6, 7, 5], [8, 8, 1, 7]])
    []
    >>> simplify_rm1_recursive([[1, 5, 2, 4], [3, 3, 4, 2], [7, 10, 8, 1], [8, 6, 9, 5], [9, 6, 10, 7]])
    [[3, 6, 4, 1], [4, 2, 5, 1], [5, 2, 6, 3]]

    Arguments:
    knot -- the PD notation of a knot
    """
    while True:
        moves_possible = check_rm1(knot)
        if moves_possible:
            simplify_rm1(moves_possible[0], moves_possible[1])
        if not moves_possible:
            break;
    return knot

# if __name__ == '__main__':
#     import doctest
#     doctest.testmod()
