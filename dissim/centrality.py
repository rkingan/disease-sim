"""

Contains methods for computing various centrality measures, or for using
built-in centrality measures in python-igraph, and a method for selecting
vertices to remove from a graph iteratively by identifying the vertex or
vertices with the highest measure.

"""
import igraph
import numpy as np
from scipy.linalg import eigh
from copy import deepcopy
from typing import Callable, Iterable


def _largest_eigenvalue(adj: np.array) -> float:
    n = adj.shape[0]
    w = eigh(adj, eigvals_only=True, subset_by_index=[n - 1, n - 1])
    return np.real(w)[0]


def compute_spread_centrality_of_matrix(adj: np.array) -> np.array:
    """
    
    Computes spread centrality of a graph given its adjacency matrix - the
    reduction in the largest eigenvalue when each vertex is removed.
    
    """
    full_largest_eig = _largest_eigenvalue(adj)
    n = adj.shape[0]
    values = []
    for i in range(n):
        min_adj = np.delete(adj, i, 0)
        min_adj = np.delete(min_adj, i, 1)
        min_largest_eig = _largest_eigenvalue(min_adj)
        values.append(full_largest_eig - min_largest_eig)

    return np.array(values).reshape(-1)


def compute_spread_centrality_of_graph(G: igraph.Graph) -> np.array:
    """
    
    Computes spread centrality of a graph - the reduction in the largest
    eigenvalue when each vertex is removed.
    
    """
    adj = np.array(G.get_adjacency().data)
    return compute_spread_centrality_of_matrix(adj)


def compute_eigenvector_centrality_of_matrix(adj: np.array) -> np.array:
    """

    Computes the eigenvector centrality of a graph given its adjacency matrix -
    the eigenvector corresponding to the graph's largest eigenvalue.

    """
    n = adj.shape[0]
    w, v = eigh(adj, subset_by_index=[n - 1, n- 1])
    raw_result = np.array(v[:, 0]).reshape(-1)
    if raw_result[0] < 0:
        raw_result = -raw_result
    return raw_result


def compute_eigenvector_centrality_of_graph(G: igraph.Graph) -> np.array:
    """

    Computes the eigenvector centrality of a graph - the eigenvector
    corresponding to the graph's largest eigenvalue.

    """
    adj = np.array(G.get_adjacency().data)
    return compute_eigenvector_centrality_of_matrix(adj)


def compute_degree_centrality_of_matrix(adj: np.array) -> np.array:
    """
    
    Returns the degree list of a graph given its adjacency matrix.
    
    """
    return np.array(np.sum(adj, 0)).reshape(-1)


def compute_degree_centrality_of_graph(G: igraph.Graph) -> np.array:
    """
    
    Returns the degree list of a graph.
    
    """
    return np.array(G.degree()).reshape(-1)


def compute_closeness_centrality_of_graph(G: igraph.Graph) -> np.array:
    """
    
    Returns the closeness centrality of a graph - obtained using its closeness
    method, then scaling by 1/n.
    
    """
    n = len(G.vs)
    scores = G.closeness()
    return (1 / n) * np.array(scores).reshape(-1)


def compute_closeness_centrality_of_matrix(adj: np.array) -> np.array:
    """
    
    Returns the closeness centrality of a graph given its adjacency matrix -
    obtained by creating an igraph.Graph instance and using its closeness
    method, then scaling by 1/n.
    
    """
    G = igraph.Graph.Adjacency((adj > 0), mode="undirected")
    return compute_closeness_centrality_of_graph(G)


def compute_betweenness_centrality_of_graph(G: igraph.Graph) -> np.array:
    """
    
    Computes the betweenness centrality of a graph - uses the igraph.Graph
    betweenness method, and converts the result to a numpy array.
    
    """
    scores = G.betweenness()
    return np.array(scores).reshape(-1)


def compute_betweenness_centrality_of_matrix(adj: np.array) -> np.array:
    """
    
    Computes the betweenness centrality of a graph given its adjacency matrix -
    creates an igraph.Graph instance from the matrix and uses its betweenness
    method, then converts the result to a numpy array.
    
    """
    G = igraph.Graph.Adjacency((adj > 0), mode="undirected")
    return compute_betweenness_centrality_of_graph(G)


def select_vertices_by_centrality_from_matrix(adj: np.array, to_select: int, centrality_ftn: Callable[[np.array], np.array], sampler: Callable[[Iterable, int], Iterable]) -> list:
    """
    
    Identifies vertices in a graph given its adjacency matrix iteratively using
    a centrality measure. The vertices having the highest centrality (there may
    be ties) are identified first. Then the function is called again with those
    vertices removed. The process proceeds until the required number of vertices
    has been selected. If there are more ties than there are vertices left to
    select, the passed sampling function is used to draw a random sample of the
    vertices to select.
    
    """
    n = adj.shape[0]
    if to_select > n:
        raise ValueError(f"Attempt to select {to_select} vertices from a graph with {n} vertices")
    cent = centrality_ftn(adj)
    max_cent = np.max(cent)
    max_inds = sorted(np.nonzero(cent == max_cent)[0])
    if len(max_inds) >= to_select:
        max_inds = sorted(sampler(max_inds, to_select))
        return max_inds

    minor_indices = [i for i in range(n) if i not in max_inds]
    minor_adj = np.delete(adj, max_inds, axis=0)
    minor_adj = np.delete(minor_adj, max_inds, axis=1)
    minor_selection = select_vertices_by_centrality_from_matrix(minor_adj, to_select - len(max_inds), centrality_ftn, sampler)
    selected_indices = [minor_indices[i] for i in minor_selection]
    return sorted(max_inds + selected_indices)


def _select_vert_by_cent_from_graph(G_labeled: igraph.Graph, to_select: int, centrality_ftn: Callable[[igraph.Graph], np.array], sampler: Callable[[Iterable, int], Iterable]) -> list:
    cent = centrality_ftn(G_labeled)
    max_cent = np.max(cent)
    max_inds = sorted(np.nonzero(cent == max_cent)[0])
    v = G_labeled.vs["_select_ind"]
    max_sel = [v[i] for i in max_inds]
    if len(max_inds) >= to_select:
        return max_sel
    G_minor = deepcopy(G_labeled)
    G_minor.delete_vertices(max_inds)
    minor_sel = _select_vert_by_cent_from_graph(G_minor, to_select - len(max_inds), centrality_ftn, sampler)
    return sorted(max_sel + minor_sel)


def select_vertices_by_centrality_from_graph(G: igraph.Graph, to_select: int, centrality_ftn: Callable[[igraph.Graph], np.array], sampler: Callable[[Iterable, int], Iterable]) -> list:
    """
    
    Identifies vertices in a graph iteratively using a centrality measure. The
    vertices having the highest centrality (there may be ties) are identified
    first. Then the function is called again with those vertices removed. The
    process proceeds until the required number of vertices has been selected. If
    there are more ties than there are vertices left to select, the passed
    sampling function is used to draw a random sample of the vertices to select.
    
    """
    n = len(G.vs)
    if to_select > n:
        raise ValueError()
    G_labeled = G.copy()
    G_labeled.vs["_select_ind"] = list(range(n))
    return _select_vert_by_cent_from_graph(G_labeled, to_select, centrality_ftn, sampler)
