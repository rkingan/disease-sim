"""

Implementations of death functions that can be used to decide when a node goes
from INFECTED to RECOVERED.

"""
from typing import Callable
from scipy.stats import norm


class NormalDeathFunction:
    """
    
    Death function where recovery time is normally distributed with a given mean
    and standard deviation.
    
    """
    def __init__(self, mu: float, sigma: float):
        self.mu = mu
        self.sigma = sigma

    def __call__(self, t, p):
        z = norm.cdf((t - self.mu) / self.sigma)
        return p < z


def generate_normal_death_ftn_factory(mu: float, sigma: float) -> Callable[[], Callable[[int, float], bool]]:
    """
    
    Returns a function that generates instances of NormalDeathFunction for each
    node with a specified mean and standard deviation.
    
    """
    def generate():
        return NormalDeathFunction(mu, sigma)

    return generate


class UniformDeathFunction:
    """
    
    Death function where recovery time is uniformly distributed between two
    values - the actual recovery time is chosen at the outset, so the random
    number is not used.
    
    """
    def __init__(self, min_t: int, max_t: int, rng: Callable[[], float]):
        r = rng()
        self.recovery_time = min_t + int((max_t - min_t) * r)

    def __call__(self, t, _):
        return t >= self.recovery_time


def generate_uniform_death_ftn_factory(min_t: int, max_t: int, rng: Callable[[], float]) -> Callable[[], Callable[[int, float], bool]]:
    """
    
    Returns a function that generates instances of UniformDeathFunction for each
    node with a specified minimum recovery time, maximum recovery time and
    random number generation function.
    
    """
    def generate():
        return UniformDeathFunction(min_t, max_t, rng)

    return generate


class SimpleBernoulliDeathFunction:
    """
    
    Death function where recovery is a simple Bernoulli trial at each time with
    a given success probability, so the time is ignored.
    
    """
    def __init__(self, prob: float):
        self.prob = prob

    def __call__(self, _, p):
        return p < self.prob


def generate_simple_bernoulli_death_ftn_factory(prob: float) -> Callable[[], Callable[[int, float], bool]]:
    """
    
    Returns a function that generates instances of SimpleBernoulliDeathFunction
    for each node with a specified probability.
    
    """
    ftn = SimpleBernoulliDeathFunction(prob)

    def generate():
        return ftn

    return generate
