[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.999015.svg)](https://doi.org/10.5281/zenodo.999015)

# Purpose
Naïvely compute an upper bound on the bridge index of knots using Reidemeister moves.

# How to use this program
## Input CSV files
The program processes planar diagram (PD) codes stored in CVS files with the headers “name” and “pd_notation”.

For example, the contents of an input CSV file named `pd_codes.csv`:
```
name,pd_notation
3_1,"[[1,5,2,4],[3,1,4,6],[5,3,6,2]]"
4_1,"[[4,2,5,1],[8,6,1,5],[6,3,7,4],[2,7,3,8]]"
5_1,"[[2,8,3,7],[4,10,5,9],[6,2,7,1],[8,4,9,3],[10,6,1,5]]"
5_2,"[[1,5,2,4],[3,9,4,8],[5,1,6,10],[7,3,8,2],[9,7,10,6]]"
```

PD codes for all prime knots with 3-12 crossings (from [KnotInfo: Table of Knot Invariants](http://www.indiana.edu/~knotinfo/)) and a few unknots are provided in the folder `pd_codes`.

## Running the program
### The easy way
The simplest way to use the program is to run the following two commands where `<path_to_input>` is replaced with the path to the input CVS file or a directory containing multiple input CSV files.

```
./bridge_computation.py -i <path_to_input>
./analyze_output.py
```

### The slightly more complicated (but more flexible) way
In addition to specifying the path to input file(s), it is also possible to specifiy a directory to store the output of `bridge_computation.py` (it defaults to “output”) by using the `-o` argument. 

If you specify a directory for the output of `bridge_computation.py`, you must also specify the input directory for `analyze_output.py` (it also defaults to “output”).

### Example

Using `pd_codes.csv` from above, running `./bridge_computation.py -i pd_codes.csv -o my/output_directory/` generates the following output structure:
```
output/
  3_1_output.csv
  4_1_output.csv
  5_1_output.csv
  5_2_output.csv
```

The contents of each output CSV file is similar to that of `output/3_1_output.csv`:
```
name,computed_bridge_index
3_1_tree_1_0,2
3_1_tree_2_0,2
3_1_tree_3_0,2
```

Then running `analyze_output.py -i my/output_directory/` outputs the file `analyzed_output/minimum_computed_bridge_indices.csv`, which contains the minimum value from the column `computed_bridge_index` of each CSV file in `my/output_directory/`.

Continuing our example, `analyzed_output/minimum_computed_bridge_indices.csv` contains:
```
knot,minimum_computed_bridge_index
3_0001,2
4_0001,2
5_0001,2
5_0002,2
```

### Note
`analyze_output.py` takes an optional argument, `--numeral_places` (which defaults to 4). This argument is used to control the number of digits to the right of the underscore in the output knot names. This is useful for sorting the final output by knot name.
