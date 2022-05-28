"""

Includes a simple random number generation function based on the built-in Python
`random` module.

"""
import random

class SimpleRNG:
    def __init__(self, seed):
        random.seed(seed)

    def __call__(self):
        return random.random()
