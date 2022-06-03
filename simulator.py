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


max_general_expected_rewards = None
max_general_expected_rewards_idx = 0
for n in range(len(expected_rewards)):
    if max_general_expected_rewards is None or expected_rewards[n] > max_general_expected_rewards:
        max_general_expected_rewards = expected_rewards[n]
        max_general_expected_rewards_idx = n


def get_label(coin):
    return rewards[coin.n_flips][coin.n_heads][0]


class SimpleModel:
    """
    SimpleModel

    Ends testing the coin when the general expected reward is at its maxima
    """

    def __init__(self, fund):
        self.fund = fund

    def end_test(self, coin: Coin):
        global max_general_expected_rewards_idx
        return self.fund == 0 or coin.n_flips >= R_if_correct - 1 or coin.n_flips >= max_general_expected_rewards_idx

    def test(self, coin: Coin):
        while not self.end_test(coin):
            self.fund -= 1
            coin.flip()

    def reward(self, coin: Coin):
        label = get_label(coin)
        if (label == "FAIR" and coin.is_fair) or (label == "CHEAT" and not coin.is_fair):
            # Correct
            self.fund += R_if_correct
            return True

        # Incorrect
        self.fund += R_if_incorrect
        return False


class ElasticModel:
    """
    ElasticModel

    Ends testing the coin if the rewards is expected to be decreased
    """

    def __init__(self, fund):
        self.fund = fund

    def end_test(self, coin: Coin):
        return self.fund == 0 or coin.n_flips >= R_if_correct - 1 or \
               rewards[coin.n_flips][coin.n_heads][1] > get_local_expected_rewards(coin.n_flips, coin.n_heads)

    def test(self, coin: Coin):
        while not self.end_test(coin):
            self.fund -= 1
            coin.flip()

    def reward(self, coin: Coin):
        label = get_label(coin)
        if (label == "FAIR" and coin.is_fair) or (label == "CHEAT" and not coin.is_fair):
            # Correct
            self.fund += R_if_correct
            return True

        # Incorrect
        self.fund += R_if_incorrect
        return False


class BiasedModel:
    """
    BiasedModel

    Ends testing the coin if the rewards is expected to be decreased; using prior
    """

    def __init__(self, fund):
        self.fund = fund

    def end_test(self, coin: Coin):
        return self.fund == 0 or coin.n_flips >= R_if_correct - 1 or \
               rewards[coin.n_flips][coin.n_heads][1] > get_local_expected_rewards_with_prior(coin.n_flips,
                                                                                              coin.n_heads)

    def test(self, coin: Coin):
        while not self.end_test(coin):
            self.fund -= 1
            coin.flip()

    def reward(self, coin: Coin):
        label = get_label(coin)
        if (label == "FAIR" and coin.is_fair) or (label == "CHEAT" and not coin.is_fair):
            # Correct
            self.fund += R_if_correct
            return True

        # Incorrect
        self.fund += R_if_incorrect
        return False


def simulation(model, prompt=False):
    score = 0
    while model.fund > 0:
        coin = Coin()
        model.test(coin)
        is_correct = model.reward(coin)

        if is_correct:
            score += 1

        if prompt:
            print(f"Score: {score}")
            print(f"Remaining: {model.fund}")
    return score


def test_model(model, num_test=100, prompt_records=False):
    global FUND
    records = []
    for _ in range(num_test):
        records.append(simulation(model))
        model.fund = FUND
    if prompt_records:
        print(records)
    return f"Min: {min(records)}, Mean: {sum(records) / len(records)}, Max: {max(records)}"


# Simulation
FUND = 100
simple_model = SimpleModel(FUND)
elastic_model = ElasticModel(FUND)
biased_model = BiasedModel(FUND)

print(f"Simple Model Result: {test_model(simple_model, 10000)}")
print(f"Elastic Model Result: {test_model(elastic_model, 10000)}")
print(f"Biased Model Result: {test_model(biased_model, 10000)}")
