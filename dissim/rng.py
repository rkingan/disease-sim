"""

Includes a simple random number generation function based on the built-in Python
`random` module.

"""
import random

class SimpleRNG:
    def __init__(self, seed):
        if seed is not None:
            random.seed(seed)

    def __call__(self):
        return random.random()


class SimpleSampler:
    def __init__(self, seed):
        if seed is not None:
            random.seed(seed)

    def __call__(self, population, k):
        return random.sample(population, k)
