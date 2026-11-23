# Red Scare! — Algorithm Design

This folder contains our implementations for the five Red Scare! questions and the instance runner used to produce [`results.txt`](results.txt).

## Requirements

- Python 3.10 or newer
- NetworkX (needed by the `Some` solver)

Install the external dependency with:

```bash
python3 -m pip install networkx
```

The other solvers use only the Python standard library.

## Recreate `results.txt`

From this directory, run:

```bash
python3 run_all.py data
```

The command processes the instance files in `data/` in filename order and overwrites `results.txt`. The output is tab-separated and has a header row. The runner accepts a different input directory as its first argument. Its output path defaults to `results.txt` in the current working directory; to choose another output path, call `main(input_directory, output_path)` from Python or change that default in `run_all.py` (the command-line interface does not currently expose an output-path option).

`run_all.py` collects one answer per instance from the five solver modules:

| Column | Question | Meaning |
| --- | --- | --- |
| `A` | Alternate | Is there an $s$–$t$ path whose adjacent vertices alternate in colour? |
| `F` | Few | Minimum number of red vertices on an $s$–$t$ path; `-1` means no path exists. |
| `M` | Many | Maximum number of red vertices on a simple $s$–$t$ path, when the implemented exact method supports the instance. |
| `N` | None | Length in edges of the shortest $s$–$t$ path that avoids red vertices, except that a red target is allowed; `-1` means no such path exists. |
| `S` | Some | Whether there is a simple $s$–$t$ path containing at least one red vertex. |

In the `M` column, `?!` means the instance falls outside the exact solver's supported graph classes; it does **not** mean that no path exists. The `S` solver may return `?` if its directed-graph search reaches its time limit. `A` and `S` are displayed as booleans (`true`/`false` for `A`, `True`/`False` for `S`).

## Solver modules

- [`rs_alternate.py`](rs_alternate.py) (`A`): breadth-first search using only edges whose endpoints have different colours.
- [`rs_few.py`](rs_few.py) (`F`): 0–1 BFS, assigning cost 1 to entering a red vertex and 0 to entering a non-red vertex.
- [`rs_many.py`](rs_many.py) (`M`): exact methods for directed acyclic graphs, undirected graphs with at most one red vertex, and undirected graphs with cycle rank at most 8. Other reachable instances are reported as unsupported (`?!`). It can also be run independently:

	```bash
	python3 rs_many.py data
	python3 rs_many.py data/G-ex.txt --output many_results.tsv
	```

- [`rs_none.py`](rs_none.py) (`N`): breadth-first search that does not enter red vertices, except when the red vertex is the target.
- [`rs_some.py`](rs_some.py) (`S`): uses NetworkX max-flow for undirected instances and simple-path search for directed instances (with a 300-second limit per directed instance).

The runner imports all five modules and writes the combined table. The `rs_none.py` and `rs_few.py` programs can also be run individually on one instance, for example:

```bash
python3 rs_none.py data/G-ex.txt
python3 rs_few.py data/G-ex.txt
```

## Instance format

The supplied graph instances are in `data/`. The solvers expect the format used by those files: a first line containing the vertex, edge, and red-vertex counts; a second line containing the source and target; one line per vertex (red vertices are marked with `*`); and one line per edge. Undirected edges use `u -- v` and directed edges use `u -> v`.

The combined runner reports errors for individual files to standard error and continues processing the remaining inputs. Check that output if a recreated result table is missing an instance.
