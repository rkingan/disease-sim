r"""

Script to run disease propagation simulations. Reads a specified graph, selects
an initial infected vertex and vertices to "vaccinate" using a specified
strategy, and then carries out a specified number of rounds of propagation.
Writes an output CSV file with parameters for each trial and the number of
infected vertices at each step in the trial.

"""
import click
import logging
import igraph
import sys
import csv
from typing import Any
from dissim.igraph_util import load_graph_here, nodes_from_igraph
from dissim.centrality import centrality_ftn, selection_strategy, SELECTION_STRATEGY_TYPE, CENTRALITY_FTN_TYPE
from dissim.main import prop_model, SISModel, DSState, propagate
from dissim.rng import SimpleSampler, SimpleRNG

logging.basicConfig(level=logging.INFO,format="[%(asctime)s] : %(filename)s[%(lineno)d] : %(levelname)s : %(message)s")
log = logging.getLogger()


def _get_trial_vaxxed(p0_ix, vaxxed):
    if len(vaxxed) == 0:
        return vaxxed
    if p0_ix in vaxxed:
        return [i for i in vaxxed if i != p0_ix]

    return vaxxed[:-1]


def _get_round_totals(nodes, rounds):
    n = len(nodes)
    totals = [0] * rounds
    for node in nodes:
        for rnd in range(rounds):
            if node.states[rnd] == DSState.INFECTED:
                totals[rnd] += 1
    return totals


@click.command("run-sim")
@click.argument("graph", type=load_graph_here)
@click.argument("output_fname", type=click.Path())
@click.option("-p", "--patient0-method", "p0", type=str, default=None, help="Name of patient 0 vertex; if not specified repeat for all vertices")
@click.option("-x", "--strategy", "strategy_name", type=str, default=None, help="Name of vaccination selection strategy")
@click.option("-c", "--centrality", "centrality_name", type=str, default=None, help="Name of centrality measure for vaccination selection")
@click.option("-f", "--percent-to-vax", "pct_vax", type=int, default=50, help="Percent (integer) of nodes to vaccinate")
@click.option("-t", "--trials", "trials",  type=int, default=100, help="Number of trials")
@click.option("-m", "--model", "model_name", type=str, default="SIS", help="Propagation model to use")
@click.option("-r", "--rounds", "rounds", type=int, default=100, help="Number of rounds to run in each trial")
@click.option("-b", "--pb", "pb", type=float, default=0.05, help="Propagation probability")
@click.option("-d", "--pd", "pd", type=float, default=0.05, help="Recovery probability")
@click.option("-z", "--seed", "rng_seed", type=int, default=42, help="Random number generation seed")
def run_sim(graph: igraph.Graph, output_fname: str, p0: str, strategy_name: str, centrality_name: str, pct_vax: int, trials: int, model_name: Any, rounds: int, pb: float, pd: float, rng_seed: int):
    n = len(graph.vs)

    strategy = selection_strategy(strategy_name)
    centrality = centrality_ftn(centrality_name)
    model = prop_model(model_name)

    if p0 is None:
        p0_list = list(range(n))
    else:
        try:
            p0_list = [graph.vs["label"].index(p0)]
        except ValueError as _:
            log.error("No vertex with name %s found in graph", p0)
            sys.exit(1)

    vaxxed = []
    sampler = SimpleSampler(rng_seed)
    rng = SimpleRNG(rng_seed)
    if strategy is not None:
        if centrality is None:
            log.error("Centrality measure must be specified in order to select vertices for vaccination")
            sys.exit(1)

        to_select = 1 + pct_vax * n // 100
        log.info("Selecting %d nodes to vaccinate (one extra to avoid patient 0)...", to_select)
        vaxxed = strategy(graph, to_select, centrality, sampler)
        log.info("...done.")

    cent = None
    if centrality is not None:
        cent = centrality(graph)
    
    results = list()
    nd = len(str(rounds))
    headings = ["graph", "patient0", "patient0_cent", "rounds", "strategy", "centrality", "model", "pb", "pd", "seed", "trial"] + [f"infected_{i:0{nd}d}" for i in range(rounds)]

    model_inst = model(pb, pd, rng)
    log.info("Starting trials...")
    p0_cent = None
    for p0_ix in p0_list:
        log.info("...starting trials with patient 0 at %d...", p0_ix)
        if cent is not None:
            p0_cent = cent[p0_ix]
        for trial in range(trials):
            if trial % 25 == 0:
                log.info("...starting trial %d...", trial)
            trial_vaxxed = _get_trial_vaxxed(p0_ix, vaxxed)
            initial_states = [DSState.UNEXPOSED] * n
            initial_states[p0_ix] = DSState.INFECTED
            for ix in trial_vaxxed:
                initial_states[ix] = DSState.VACCINATED
            nodes = nodes_from_igraph(graph, initial_states)
            for rnd in range(rounds):
                propagate(nodes, model_inst)
            totals = _get_round_totals(nodes, rounds)
            results.append([graph["name"], p0_ix, p0_cent, rounds, strategy_name, centrality_name, model_name, pb, pd, rng_seed, trial] + totals)
            if trial % 25 == 0:
                log.info("...done with trial %d...", trial)
        log.info("...done with trials with patient 0 at %d...", p0_ix)
    log.info("...done.")

    log.info("Writing totals to %s...", output_fname)
    with open(output_fname, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headings)
        for rec in results:
            writer.writerow(rec)
    log.info("...done.")


if __name__ == "__main__":
    run_sim()
