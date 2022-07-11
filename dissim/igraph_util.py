"""

Utility functions for working with igraph Graph representations.

"""
import pathlib
from typing import Iterable, Dict, Callable
from igraph import Graph
from dissim.main import DSNode, DSState


_DEFAULT_COLOR_MAP = {
    DSState.UNEXPOSED: "white",
    DSState.INFECTED: "red",
    DSState.RECOVERED: "green",
    DSState.VACCINATED: "blue"
}


def nodes_from_igraph(G: Graph, initial_states: Iterable[DSState]) -> Iterable[DSNode]:
    """

    Builds a list of DSNode instances from the vertices and edges in a graph
    represented as an igraph Graph object, and a list of their initial states.

    """

    if len(G.vs) != len(initial_states):
        raise ValueError("Number of initial states must match the number of vertices in the graph.")

    n = len(G.vs)
    nodes = []
    for i in range(n):
        node = DSNode(G.vs["label"][i], initial_states[i])
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
    return [color_map[node.states[t]] for node in nodes]


_GRAPHS_DIR = pathlib.Path(__file__).resolve().parent.parent / "graphs"


def _get_gpath(name: str) -> pathlib.Path:
    return _GRAPHS_DIR / f"{name}.gml"



def load_graph_here(name: str) -> Graph:
    r"""
    
    Loads a graph by name from the "graphs" directory of this repository.
    
    """
    gpath = _get_gpath(name)
    if not(gpath.exists()):
        raise ValueError(f"No graph found with name {name}")
    g = Graph.Read_GML(str(gpath))
    g["name"] = name
    return g    
