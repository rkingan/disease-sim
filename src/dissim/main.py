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
    def __init__(self, label: str, initial_state: DSState):
        self.label = label
        self.states = [initial_state]
        self.neighbors = []
        self.time_infected = 0

    def set_new_state(self, state: DSState):
        """

        Sets new state of the node.

        """
        if state == DSState.INFECTED:
            self.time_infected += 1
        else:
            self.time_infected = 0
        self.states.append(state)

    def get_state(self) -> DSState:
        """

        Returns the current state of this node.

        """
        return self.states[-1]

    def count_infected_neighbors(self) -> int:
        return sum(1 if nbr.get_state() == DSState.INFECTED else 0 for nbr in self.neighbors)


class PropModel:
    """
    
    Empty base class for propagation models.
    
    """
    pass


class SISModel(PropModel):
    """

    SIS propagation model - a non-vaxxed node's initial state is UNEXPOSED. An
    UNEXPOSED node becomes INFECTED with probability pb for k trials, where k is
    the number of infected neighbors. An INFECTED node becomes UNEXPOSED with
    probability pd.

    """
    def __init__(self, pb: float, pd: float, rng: Callable[[], float]):
        self.pb = pb
        self.pd = pd
        self.rng = rng

    def apply(self, cur_state: DSState, k: int, dur: int) -> DSState:
        if cur_state == DSState.UNEXPOSED:
            if any(self.rng() < self.pb for _ in range(k)):
                return DSState.INFECTED
        elif cur_state == DSState.INFECTED:
            if self.rng() < self.pd:
                return DSState.UNEXPOSED
        return cur_state


class SIRModel(PropModel):
    """
    
    SIR propagation model - a non-vaxxed node's initial state is UNEXPOSED. An
    UNEXPOSED node becomes INFECTED with probability ps for k trials, where k is
    the number of infected neighbors. An INFECTED node becomes RECOVERED with
    probability pd.
    
    """
    def __init__(self, pb: float, pd: float, rng: Callable[[], float]):
        self.pb = pb
        self.pd = pd
        self.rng = rng

    def apply(self, cur_state: DSState, k: int, dur: int) -> DSState:
        if cur_state == DSState.UNEXPOSED:
            if any(self.rng() < self.pb for _ in range(k)):
                return DSState.INFECTED
        elif cur_state == DSState.INFECTED:
            if self.rng() < self.pd:
                return DSState.RECOVERED
        return cur_state


_MODELS = {
    "SIS": SISModel,
    "SIR": SIRModel
}


def prop_model(name):
    if name not in _MODELS:
        raise ValueError(f"No model with name {name} found, valid names are: {', '.join(_MODELS.keys())}")
    return _MODELS[name]


def propagate(
    nodes: Iterable[DSNode],
    model: PropModel
    ):
    """

    Applies a model to propagate states in a collection of nodes

    """

    new_states = []
    for node in nodes:
        k = node.count_infected_neighbors()
        dur = node.time_infected
        cur_state = node.get_state()
        ns = model.apply(cur_state, k, dur)
        new_states.append(ns)

    ix = 0
    for node in nodes:
        node.set_new_state(new_states[ix])
        ix += 1
