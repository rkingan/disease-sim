"""

Contains code for the DSNode object class and methods for doing disease propagation.

"""
import random
from enum import Enum
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
    if DSState.VACCINATED in (state1, state2):
        return DSState.VACCINATED

    if DSState.RECOVERED in (state1, state2):
        return DSState.RECOVERED

    if DSState.INFECTED in (state1, state2):
        return DSState.INFECTED

    return DSState.UNEXPOSED


class DSNode:
    """

    Represents one node in the network, including a label, a list of its states
    at each point in time, and a list of neighbors.

    """
    def __init__(self, label: str, initial_state: DSState, death_ftn: Callable[[int, float], bool]):
        self.label = label
        self.states = [initial_state]
        self.neighbors = []
        self.death_ftn = death_ftn

    def check_recovery(self, t: int, r: float):
        ns = len(self.states)
        if t < ns:
            raise ValueError(f"New state for time {t} is already set for node {self.label}")
        curr_state = self.states[-1]
        if curr_state != DSState.INFECTED:
            self.states.append(curr_state)
        else:
            recovered = self.death_ftn(t, r)
            if recovered:
                self.states.append(DSState.RECOVERED)
            else:
                self.states.append(curr_state)

    def set_new_state(self, state: DSState):
        """

        Sets new state of the node, or at least contributes to it.

        """
        self.states[-1] = combine_states(self.states[-1], state)

    def get_state(self, t: int) -> DSState:
        """

        Returns the state of this node at a specific time.

        """
        ns = len(self.states)
        if t < ns:
            return self.states[t]
        if t == ns:
            return None

        raise IndexError(f"Attempt to get state at time {t}, only {ns} states exist")


def propagate(
    nodes: Iterable[DSNode],
    t: int,
    ps: float,
    rng: Callable[[], float]
    ):
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

    for node in nodes:
        r = rng()
        node.check_recovery(t, r)

    for node in nodes:
        if node.get_state(t - 1) == DSState.INFECTED:
            #
            # each other node gets infected with probability ps
            #
            for nbr in node.neighbors:
                r = rng()
                if r < ps:
                    nbr.set_new_state(DSState.INFECTED)


def iterate(
    nodes: Iterable[DSNode],
    nt: int,
    ps: float,
    rng: Callable[[], float] = random.random
    ):
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
        propagate(nodes, t, ps, rng)
