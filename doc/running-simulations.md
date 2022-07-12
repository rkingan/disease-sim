# Running simulations using `sim.py`

This repository contains a module called `sim` which can run disease propagation
simulations. It allows you to choose a graph in which to operate, specify a
strategy for "vaccinating" certain nodes in the graph, and also to specify the
values of parameters relevant to the propagation simulations.

To run the program you first need to have this repository installed in your
current Python environment. The easiest way to do this is via the `pip` command.
In a command window, navigate to the main directory of this repository, and
enter the following command:

```bash
pip install -e .
```

Make sure you include the dot at the end. This tells `pip` to install the
package in this repository in "editable" mode, which means that any changes you
make to the code in your working copy of the repository will be immediately
reflected when you run modules with python.

In order to check that the installation completed successfully, run this command:

```bash
python -m dissim.sim --help
```

If everything worked correctly you should see the following output:

```
Usage: python -m dissim.sim [OPTIONS] GRAPH OUTPUT_FNAME

Options:
  -p, --patient0-method TEXT    Comma-separated names of seed vertices; if not
                                specified repeat for all vertices
  -x, --strategy TEXT           Name of vaccination selection strategy
  -c, --centrality TEXT         Name of centrality measure for vaccination
                                selection
  -f, --percent-to-vax INTEGER  Percent (integer) of nodes to vaccinate
  -t, --trials INTEGER          Number of trials
  -m, --model TEXT              Propagation model to use
  -r, --rounds INTEGER          Number of rounds to run in each trial
  -b, --pb FLOAT                Propagation probability
  -d, --pd FLOAT                Recovery probability
  -z, --seed INTEGER            Random number generation seed
  --help                        Show this message and exit.
  ```

This output lists two required command line arguments, GRAPH and OUTPUT_FNAME,
and also lists a number of optional arguments. All of these arguments are
described in detail below.

## Required arguments

The two arguments that are required in order to run the program, GRAPH and OUTPUT_FNAME, should be included after any options you specify.

### Choosing a GRAPH for the simulation

This argument is the name of a graph to use in the simulation, and
refers to the name of a .gml file stored in the "graphs" directory of this
repository. There are currently two files in that directory:

* `karate.gml` - This is a copy of the [Zachary's karate
  club](https://en.wikipedia.org/wiki/Zachary%27s_karate_club) graph, which
  describes friendships among the 34 members of a karate club. This graph has 78
  edges. In this file, the vertices are named "v0" through "v33" in no
  particular order.

* `football.gml` - This is a copy of a [network of American football games
  between Division IA colleges during the regular season in Fall
  2000](http://www-personal.umich.edu/~mejn/netdata/football.zip). This graph
  has 115 vertices and 613 edges. In this graph, the vertices are named with the
  names of the teams, with spaces removed. For example the name of the vertex
  for Florida State University is "FloridaState".

### Specifying an output file using OUTPUT_FNAME

This argument is simply the name of the file in which the program will store its
output. The output file will be in comma-separated value (CSV) format, so it is
probably a good idea to provide a filename that ends with ".csv" so that other
programs will recognize the format of the file. The contents of the output file
are described in detail below.

These are the only two things that are _required_ to be specified on the command
line. For example, if you want to run a simulation on the karate graph with
output stored in a file called `karate-output.csv` and use default values for
all of the options, the command to do this is:

```bash
python -m dissim.sim karate karate-output.csv
```

## Options

There are four options that control the initial setup of the simulation, five
more that control how the simulation runs, and one that ensures that simulations
can be run consistently.

### Setup options

#### Selecting the first infected vertices

* `-p` or `--patient0-method`

Before each simulation run can begin, the first "patients", that is vertices, to
be "infected" need to be identified. This option allows you to control the
selection of the first patients. You can specify one or more vertex names,
separated by commas. If you do not specify a value for this option, the program
will run _n_ separate sets of trials, where _n_ is the number of vertices, one
with each vertex selected as the first to be infected. If you use this option
and specify more than one vertex, do not include any spaces in between the
vertex names, just commas.

##### Example

In order to run a simulation on the karate graph using vertices v1 and v33 as the first to be infected, and write the output to a file called `karate-33-output.csv`, enter the following command:

```bash
python -m dissim.sim -p v1,v33 karate karate-33-output.csv
```

#### Selecting vertices to "vaccinate"

* `-x` or `--strategy`
* `-c` or `--centrality`
* `-f` or `--percent-to-vax`

These options, together, allow you to select a number of vertices to mark as
"vaccinated" prior to running the simulation. Vaccinated vertices are
essentially removed from the graph - they cannot become infected or spread an
infection. 

The `-f` option specifies how the number of vertices to be vaccinated should be
calculated. It should be a whole number between 1 and 99, inclusive, and will be
used as a percentage to compute the number _k_ of vertices to vaccinate. The
default value of `-f` is 50.

There are two strategies, or values for `-x`, to choose from: 

* "batch" - If this option is selected, the vertices selected to be vaccinated
  are just the ones with the top _k_ centrality values.
* "recursive" - If this option is selected, the vertex with the highest
  centrality value will be removed first, then the vertex with the highest value
  in the remaining graph will be removed, and so on until _k_ vertices have been
  removed.

The allowable options for `-c`, the centrality measure are:

* "spread" - Spread centrality
* "eigenvector" - Eigenvector centrality
* "degree" - degree centrality
* "closeness" - closeness centrality
* "betweenness" - betweenness centrality

##### Example

In order to select 25% of vertices in the karate graph to vaccinate, using
eigenvector centrality and the recursive strategy, writing output to a file
called `karate-25-eig-recursive.csv`, enter the following command:

```bash
python -m dissim.sim -f 25 -x eigenvector -c recursive karate karate-25-eig-recursive.csv
```

