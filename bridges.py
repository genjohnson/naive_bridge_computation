#!/usr/bin/env python2.7

def remove_tuple(tuple, knot):
  print 'the tuple to be removed from the knot ' + str(knot) + ' is ' + str(tuple)

def has_twist(tuple):
  duplicate_value = has_duplicate_value(tuple)
  if duplicate_value:
    return True
  else:
    return False

    # If two elements in the tuple are equal (with value x)
      # Delete the tuple
      # Decrease all elements with value greater than x
      # print "The tuple [] has been eliminated"
  # return knot  

def has_duplicate_value(tuple):
  sets = reduce(
    lambda (u, d), o : (u.union([o]), d.union(u.intersection([o]))),
    tuple,
    (set(), set()))

  if sets[1]:
    return sets[1]
  else:
    return False

def simplify_all_rm1(knot):
  for tuple in knot:
    if has_duplicate_value(tuple):
      remove_tuple(tuple, knot)
  return knot

# Read in a CSV.
import ast
import csv
with open('knots.csv') as csvfile:
  fieldnames = ['name', 'pd_notation']
  knotreader = csv.DictReader(csvfile)

  for row in knotreader:
    # Evaluate strings containing Python lists.
    knot = ast.literal_eval(row['pd_notation'])
    # Check if the knot contains any twists.
    simplify_all_rm1(knot)
