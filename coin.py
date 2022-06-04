from random import random
from compute_probabilities import *


def flip_fair_coin():
    return random() < P_FAIR


def flip_cheat_coin():
    return random() < P_CHEAT


def fair_or_cheat():
    return random() < P_IS_FAIR


class Coin:
    def __init__(self):
        self.is_fair = fair_or_cheat()
        self.n_flips = 0
        self.n_heads = 0

    def flip(self):
        self.n_flips += 1
        if self.is_fair:
            is_head = flip_fair_coin()
            if is_head:
                self.n_heads += 1
                return True

            return False

        is_head = flip_cheat_coin()
        if is_head:
            self.n_heads += 1
            return True

        return False
