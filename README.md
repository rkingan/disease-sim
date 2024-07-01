# disease-sim - A simple Python simulation of disease progression

This project contains code for a simple disease progression simulation that is
designed to begin with a graph indicating connections between people and some
other initial state (such as which people are vaccinated and who is "patient 0")
variables, and then simulates how a disease progresses through the network,
given specific values of _p<sub>s</sub>_ and _p<sub>d</sub>_.

## Setting up this library for development

Instructions are included below for setting up the library using Anaconda, or pip.

### Anaconda

1. First make sure you have Anaconda installed on your system. It can be obtained
[here](https://www.anaconda.com/download).

2. Open a command line window via Anaconda (if using the Anaconda Windows distribution) or a regular command line
   otherwise and navigate to the directory containing your working copy of this repository.

3. Run the following commands to set up an environment for this project and install dependencies:

```bash
conda create -n dissim "python >= 3.8" --file requirements.txt
conda update -n dissim --freeze-installed --file requirements-dev.txt
```

4. Run the following command to add this environment to the selections available in Jupyter notebooks:

```bash
python -m ipykernel install --user --name=dissim
```

5. Run the following commands to make the code in this repository available in the `dissim` environment:

```bash
conda install pip
pip install -e .
```

### pip

1. Make sure you have at least version 3.8 of Python installed and runnable from the command line. Also make sure that
   you have the ability to create virtual environments. For the last step, you also need to make sure you have Jupyter
   notebook or Jupyter lab available.

2. Open a command line window and navigate to the directory containing your working copy of this repository.

3. Run the following commands to create a virtual environment for this project (the command you use to run Python may
   differ - for example, I use "python3.11"):

```bash
python3.8 -m venv ./.venv
source ./.venv/bin/activate
pip install --upgrade pip setuptools wheel
```

4. Run the following command to install this project and its dependencies in the virtual environment:

```bash
pip install -e .
```

5. Run the following command to add this virtual environment to the list of options in Jupyter:

```bash
python -m ipykernel install --user --name=dissim
```
