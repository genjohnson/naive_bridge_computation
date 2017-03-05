#!/usr/bin/env python2.7

# Read in a CSV.
import csv
with open('knots.csv') as csvfile:
  fieldnames = ['name', 'pd_notation']
  knotreader = csv.DictReader(csvfile)
  for row in knotreader:
    print(row)
