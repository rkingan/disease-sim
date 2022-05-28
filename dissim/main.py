"""

Contains code for the DSNode object class and methods for doing disease propagation.

"""
import random
from enum import Enum
from tkinter import E
from typing import Callable, Iterable


class DSState(Enum):
    """
    
    Represents the possible states of a node.
    
    """
    UNEXPOSED = 0
    INFECTED = 1
    RECOVERED = 2
    VACCINATED = 3


def combine_states(state1: DSState, state2: DSState) -> DSState:
    """
    
    Combines two states, used when multiple neighbors assign a new state to a
    node.
    
    """
    if state1 == DSState.VACCINATED or state2 == DSState.VACCINATED:
        return DSState.VACCINATED
    
    if state1 == DSState.RECOVERED or state2 == DSState.RECOVERED:
        return DSState.RECOVERED
    
    if state1 == DSState.INFECTED or state2 == DSState.INFECTED:
        return DSState.INFECTED

    return DSState.UNEXPOSED


class DSNode:
    """
    
    Represents one node in the network, including a label, a list of its states
    at each point in time, and a list of neighbors.
    
    """
    def __init__(self, label: str, initial_state: DSState):
        self.label = label
        self.states = [initial_state]
        self.neighbors = []

    def set_new_state(self, t: int, state: DSState):
        ns = len(self.states)
        if t != ns and t != ns - 1:
            raise RuntimeError(f"Attempt to set state at time {t} when there are {ns} previous states")
        if ns >= len(self.states):
            self.states.append(state)
        else:
            self.states[-1] = combine_states(self.states[-1], state)

    def get_state(self, t: int) -> DSState:
        ns = len(self.states)
        if t < ns:
            return self.states[t]
        if t == ns:
            return None

        raise IndexError(f"Attempt to get state at time {t}, only {ns} states exist")
            


def propagate(node: DSNode, t: int, ps: float, death_ftn: Callable[[int, float], bool], rng: Callable[[], float]):
    """
   
    Propagates state from a node to its neighbors.

    node - the node whose neighbors need updated 
    
    t - the time point being set (i.e. the "next" time) 
    
    ps - probability of spreading the infection to an uninfected, unvaccinated
    node
    
    death_ftn - function that accepts the time t and a random number in the
    range [0, 1] and returns a boolean indicating if the virus dies at this
    point

    rng - random number generating function
    
    """
    if node.get_state() == DSState.INFECTED:
        # 
        # virus may die in this node; if so it does non infect any other nodes
        #
        r = rng()
        d = death_ftn(t, r)
        if d:
            node.set_new_state(t, DSState.RECOVERED)
        else:
            #
            # each other node gets infected with probability ps
            #
            for nbr in node.neighbors:
                r = rng()
                if r < ps:
                    nbr.set_new_state(t, DSState.INFECTED)


def iterate(nodes: Iterable[DSNode], nt: int, ps: float, death_ftn: Callable[[int, float], bool], rng: Callable[[], float] = random.random):
    """
    
    Runs propagation for nt rounds, assuming nodes have already been set up with
    time 0 states.

    nodes - the nodes in the graph

    nt - the number of rounds

    ps - probability of spreading the infection to an uninfected, unvaccinated
    node
    
    death_ftn - function that accepts the time t and a random number in the
    range [0, 1] and returns a boolean indicating if the virus dies at this
    point

    rng - random number generating function
    
    """
    for t in range(1, 1 + nt):
        for node in nodes:
            propagate(node, t, ps, death_ftn, rng)
