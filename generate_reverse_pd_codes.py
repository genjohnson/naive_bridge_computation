#!/usr/bin/env python2.7

import ast
import csv
import sys, getopt

def generate_reverse_pd_codes(argv):
  """
  Switch between clockwise and counterclockwise traversal of segments for
  generation of PD codes.
  This is useful when using PD codes between Knotinfo and Sage.
  """
  inputfile = ''
  try:
      opts, args = getopt.getopt(argv,"hi:o:",["inputfile="])
  except getopt.GetoptError:
      print 'generate_reverse_pd_codes.py -i <inputfile>'
      sys.exit(2)
  for opt, arg in opts:
      if opt == '-h':
          print 'generate_reverse_pd_codes.py -i <inputfile>'
          sys.exit()
      elif opt in ("-i", "--inputfile"):
          inputfile = arg

  inputfile = open(inputfile, "r")
  reader = csv.DictReader(inputfile)
  outfile = open('pd_codes/sage.csv', "w")
  writer = csv.writer(outfile, delimiter=',')
  writer.writerow(['name','pd_notation'])

  for row in reader:
    pd_code = ast.literal_eval(row['pd_notation'])
    sage_pd_code = []
    for crossing in pd_code:
      a,b,c,d = crossing
      sage_pd_code.append([a,d,c,b])
    name = 'sage_' + row['name']
    writer.writerow([name, sage_pd_code])

  inputfile.close()
  outfile.close()

if __name__ == "__main__":
  generate_reverse_pd_codes(sys.argv[1:])
