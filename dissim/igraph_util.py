"""

Utility functions for working with igraph Graph representations.

"""
from typing import Iterable, Dict, Callable
from igraph import Graph
from dissim.main import DSNode, DSState


_DEFAULT_COLOR_MAP = {
    DSState.UNEXPOSED: "white",
    DSState.INFECTED: "red",
    DSState.RECOVERED: "green",
    DSState.VACCINATED: "blue"
}


def nodes_from_igraph(G: Graph, initial_states: Iterable[DSState], death_ftn_factory: Callable[[], Callable[[int, float], bool]]) -> Iterable[DSNode]:
    """

    Builds a list of DSNode instances from the vertices and edges in a graph
    represented as an igraph Graph object, and a list of their initial states.

    """

    if len(G.vs) != len(initial_states):
        raise ValueError("Number of initial states must match the number of vertices in the graph.")

    n = len(G.vs)
    nodes = []
    for i in range(n):
        node = DSNode(G.vs["label"][i], initial_states[i], death_ftn_factory())
        nodes.append(node)

    for edge in G.es:
        src = edge.source
        tar = edge.target

        nodes[src].neighbors.append(nodes[tar])
        nodes[tar].neighbors.append(nodes[src])

    return nodes


def colors_from_nodes(
    nodes: Iterable[DSNode],
    t: int,
    color_map: Dict[DSState, str] = _DEFAULT_COLOR_MAP
    ) -> Iterable[str]:
    """

    Returns a list of colors to plot a graph at time t based on the state of
    each node in the graph at that time.

    """
    return [color_map[node.get_state(t)] for node in nodes]
