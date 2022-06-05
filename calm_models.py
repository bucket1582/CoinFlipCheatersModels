from compute_probabilities import *
from basic_models import AbstractModel, WeakBeliefModel, FanaticModel, BeliefModel
from coin import Coin


def get_label(n_flips: int, n_heads: int) -> float:
    return labels[n_flips][n_heads]


# noinspection PyMethodMayBeStatic
class AbstractCalmModel(AbstractModel):
    """
    An abstract model for calm models

    calm models do not label coins if the end condition of testing was first met.
    """

    def __init__(self, fund: int):
        super().__init__(fund)
        self.test_phase = 0

    def calm_end_condition(self, n_flips: int, n_heads: int) -> bool:
        if self.end_condition(n_flips, n_heads) and self.test_phase == 0:
            self.test_phase = 1
            return False

        if self.end_condition(n_flips, n_heads):
            return True

        return False

    def is_end_condition(self, coin: Coin) -> bool:
        if self.fund <= 0 or coin.n_flips >= R_if_correct - 1 or self.calm_end_condition(coin.n_flips, coin.n_heads):
            self.test_phase = 0
            return True

        return False


class CalmWeakBeliefModel(AbstractCalmModel):
    """
    CalmWeakBeliefModel

    Ends testing the coin if the reward is expected to be decreased.
    For computing next head probability, this model uses p_is_fair to compute the probability of the coin to be fair.
    Means that this model uses prior data only; there is no update.
    """

    def end_condition(self, n_flips: int, n_heads: int) -> bool:
        return expected_rewards[n_flips][n_heads] > WeakBeliefModel.expect_next_reward(n_flips, n_heads)


class CalmFanaticModel(AbstractCalmModel):
    """
    CalmFanaticModel

    Ends testing the coin if the reward is expected to be decreased.
    For computing next head probability, this model uses p_fair if the model considers current coin to more likely to
    be fair, and p_cheat otherwise.
    Means that this model believes *fanatically* the observed data; the model does not use prior data.
    """

    def end_condition(self, n_flips: int, n_heads: int) -> bool:
        return expected_rewards[n_flips][n_heads] > FanaticModel.expect_next_reward(n_flips, n_heads)


class CalmBeliefModel(AbstractCalmModel):
    """
    CalmBeliefModel

    Ends testing the coin if the reward is expected to be decreased.
    For computing next head probability, this model uses fairness to compute the probability of the coin to be fair.
    Means that this model uses both prior and posterior data.
    """

    def end_condition(self, n_flips: int, n_heads: int) -> bool:
        return expected_rewards[n_flips][n_heads] > BeliefModel.expect_next_reward(n_flips, n_heads)
