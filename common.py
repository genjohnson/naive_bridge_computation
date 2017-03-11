#!/usr/bin/env python2.7

def alter_elements_greater_than(knot, value, increment):
    """Change the value of elements in the PD notation of a knot
    which are greater than some value.

    >>> alter_elements_greater_than([[4, 2, 5, 1], [8, 6, 1, 5], [6, 3, 7, 4], [2, 7, 3, 8]], 4, -2)
    [[4, 2, 3, 1], [6, 4, 1, 3], [4, 3, 5, 4], [2, 5, 3, 6]]
    >>> alter_elements_greater_than([[4, 2, 5, 1], [8, 6, 1, 5], [6, 3, 7, 4], [2, 7, 3, 8]], 4, 2)
    [[4, 2, 7, 1], [10, 8, 1, 7], [8, 3, 9, 4], [2, 9, 3, 10]]

    Arguments:
    knot -- the knot in which to alter elements
    value -- the integer against which to compare each element
    increment -- the integer to add to all elements greater than value
    """
    for place, crossing in enumerate(knot):
        for index, element in enumerate(crossing):
            if element > value:
                crossing[index] = element + increment
    return knot

def remove_tuples(indices, knot):
    """Remove tuples from the PD notation of a knot.

    >>> remove_tuples([1,3], [[4, 2, 5, 1], [8, 6, 1, 5], [6, 3, 7, 4], [2, 7, 3, 8]])
    [[4, 2, 5, 1], [6, 3, 7, 4]]

    Arguments:
    indices -- the list of indices of the tuples to remove
    knot -- the knot from which to remove tuples
    """
    # Remove tuples from last to first to avoid changing
    # the index of tuples not yet processed.
    indices.sort(reverse = True)
    for index in indices:
        del(knot[index])
    return knot
