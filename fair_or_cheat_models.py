from compute_probabilities import *
from typing import Union, Literal
from coin import Coin


def get_label(n_flips: int, n_heads: int) -> float:
    return labels[n_flips][n_heads]


# noinspection PyMethodMayBeStatic
class AbstractModel:
    """
    An abstract model for all models
    """

    def __init__(self, fund: int):
        self.fund = fund

    @classmethod
    def expect_next_reward(cls, n_flips: int, n_heads: int) -> float:
        return 0.0

    def end_condition(self, n_flips: int, n_heads: int) -> bool:
        """
        Returns if the model would end testing the coin with after [n_flips] flips and getting [n_heads] heads.
        Does not consider the model's fund or etc

        :param n_flips: Number of flips
        :param n_heads: Number of heads
        :return: Boolean value if the test ends
        """
        return True

    def is_end_condition(self, coin: Coin) -> bool:
        """
        Returns if the model would end testing for the given coin.
        Consider model's fund.

        :param coin: Tested coin
        :return: If the model would end testing
        """
        return self.fund <= 0 or coin.n_flips >= R_if_correct - 1 or self.end_condition(coin.n_flips, coin.n_heads)

    def feed(self, n_flips: int, n_heads: int) -> Union[Literal["FAIR"], Literal["CHEAT"], Literal["TEST"]]:
        """
        The model's recommendation for one of three
        1. Conclude the coin to be fair
        2. Conclude the coin to be biased
        3. Keep testing

        :param n_flips: Number of flips
        :param n_heads: Number of heads
        :return:
        FAIR if the model would conclude the coin as fair
        CHEAT if the model would conclude the coin as biased
        TEST if the model would keep testing
        """
        if self.end_condition(n_flips, n_heads):
            return labels[n_flips][n_heads]

        if n_flips >= R_if_correct - 1:
            return labels[n_flips][n_heads]

        return "TEST"

    def build_cheat_sheet(self):
        cheat_sheet = [["X" for _ in range(R_if_correct + 1)] for _ in range(R_if_correct + 1)]
        for num_flips in range(R_if_correct + 1):
            for num_heads in range(num_flips + 1):
                cheat_sheet[num_flips][num_heads] = self.feed(num_flips, num_heads)
        return cheat_sheet

    def test(self, coin: Coin) -> None:
        """
        Test the coin until the end condition meets.

        :param coin: The coin to be tested.
        """
        while not self.is_end_condition(coin):
            self.fund -= 1
            coin.flip()

    def reward(self, coin: Coin) -> bool:
        """
        Reward the model.

        :param coin: Tested coin
        :return: If the model got correct answer
        """
        label = get_label(coin.n_flips, coin.n_heads)
        if (label == "FAIR" and coin.is_fair) or (label == "CHEAT" and not coin.is_fair):
            # Correct
            self.fund += R_if_correct
            return True

        # Incorrect
        self.fund += R_if_incorrect
        return False


class NoBeliefModel(AbstractModel):
    """
    NoBeliefModel

    Ends testing the coin when the general expected reward is at its maximum.
    """
    max_general_expected_rewards = None
    max_general_expected_rewards_idx = 0
    for n in range(len(g_expected_rewards)):
        if max_general_expected_rewards is None or g_expected_rewards[n] > max_general_expected_rewards:
            max_general_expected_rewards = g_expected_rewards[n]
            max_general_expected_rewards_idx = n

    def end_condition(self, n_flips: int, n_heads: int) -> bool:
        return n_flips >= NoBeliefModel.max_general_expected_rewards_idx


class WeakBeliefModel(AbstractModel):
    """
    WeakBeliefModel

    Ends testing the coin if the reward is expected to be decreased.
    For computing next head probability, this model uses p_is_fair to compute the probability of the coin to be fair.
    Means that this model uses prior data only; there is no update.
    """

    @classmethod
    def expect_next_reward(cls, n_flips: int, n_heads: int) -> float:
        next_head_prob = P_IS_FAIR * P_FAIR + (1 - P_IS_FAIR) * P_CHEAT
        return next_head_prob * expected_rewards[n_flips + 1][n_heads + 1] + \
               (1 - next_head_prob) * expected_rewards[n_flips + 1][n_heads]

    def end_condition(self, n_flips: int, n_heads: int) -> bool:
        return expected_rewards[n_flips][n_heads] > WeakBeliefModel.expect_next_reward(n_flips, n_heads)


class CalmWeakBeliefModel(AbstractModel):
    """
    CalmWeakBeliefModel

    Ends testing the coin if the reward is expected to be decreased; but if its for the first time, it keep testing.
    For computing next head probability, this model uses p_is_fair to compute the probability of the coin to be fair.
    Means that this model uses prior data only; there is no update.
    """

    def __init__(self, fund):
        super().__init__(fund)
        self.test_phase = 0

    @classmethod
    def expect_next_reward(cls, n_flips: int, n_heads: int) -> float:
        next_head_prob = P_IS_FAIR * P_FAIR + (1 - P_IS_FAIR) * P_CHEAT
        return next_head_prob * expected_rewards[n_flips + 1][n_heads + 1] + \
               (1 - next_head_prob) * expected_rewards[n_flips + 1][n_heads]

    def end_condition(self, n_flips: int, n_heads: int) -> bool:
        if expected_rewards[n_flips][n_heads] > WeakBeliefModel.expect_next_reward(n_flips, n_heads) and \
                self.test_phase == 0:
            self.test_phase = 1
            return False

        if expected_rewards[n_flips][n_heads] > WeakBeliefModel.expect_next_reward(n_flips, n_heads):
            return True

    def is_end_condition(self, coin: Coin) -> bool:
        if self.fund <= 0 or coin.n_flips >= R_if_correct - 1 or self.end_condition(coin.n_flips, coin.n_heads):
            self.test_phase = 0
            return True

        return False


class FanaticModel(AbstractModel):
    """
    FanaticModel

    Ends testing the coin if the reward is expected to be decreased.
    For computing next head probability, this model uses p_fair if the model considers current coin to more likely to
    be fair, and p_cheat otherwise.
    Means that this model believes *fanatically* the observed data; the model does not use prior data.
    """

    @classmethod
    def expect_next_reward(cls, n_flips: int, n_heads: int) -> float:
        if labels[n_flips][n_heads] == "FAIR":
            return P_FAIR * expected_rewards[n_flips + 1][n_heads + 1] + \
                   (1 - P_FAIR) * expected_rewards[n_flips + 1][n_heads]

        return P_CHEAT * expected_rewards[n_flips + 1][n_heads + 1] + \
               (1 - P_CHEAT) * expected_rewards[n_flips + 1][n_heads]

    def end_condition(self, n_flips: int, n_heads: int) -> bool:
        return expected_rewards[n_flips][n_heads] > FanaticModel.expect_next_reward(n_flips, n_heads)


class SincereFanaticModel(FanaticModel):
    """
    SincereFanaticModel

    Ends testing the coin if the reward is expected to be decreased; but *sincerely* observes for 5 flips.
    For computing next head probability, this model uses p_fair if the model considers current coin to more likely to
    be fair, and p_cheat otherwise.
    Means that this model believes *fanatically* the observed data; the model does not use prior data.

    Note that -- the number 5 was set empirically
    """

    def end_condition(self, n_flips: int, n_heads: int) -> bool:
        return expected_rewards[n_flips][n_heads] > FanaticModel.expect_next_reward(n_flips, n_heads) and n_flips > 5


class CalmFanaticModel(FanaticModel):
    """
    CalmFanaticModel

    Ends testing the coin if the reward is expected to be decreased; but if its for the first time, it keep testing.
    For computing next head probability, this model uses p_fair if the model considers current coin to more likely to
    be fair, and p_cheat otherwise.
    Means that this model believes *fanatically* the observed data; the model does not use prior data.
    """

    def __init__(self, fund):
        super().__init__(fund)
        self.test_phase = 0

    def end_condition(self, n_flips: int, n_heads: int) -> bool:
        if expected_rewards[n_flips][n_heads] > FanaticModel.expect_next_reward(n_flips, n_heads) and \
                self.test_phase == 0:
            self.test_phase = 1
            return False

        if expected_rewards[n_flips][n_heads] > FanaticModel.expect_next_reward(n_flips, n_heads):
            return True

    def is_end_condition(self, coin: Coin) -> bool:
        if self.fund <= 0 or coin.n_flips >= R_if_correct - 1 or self.end_condition(coin.n_flips, coin.n_heads):
            self.test_phase = 0
            return True

        return False


class BeliefModel(AbstractModel):
    """
    BeliefModel

    Ends testing the coin if the reward is expected to be decreased.
    For computing next head probability, this model uses fairness to compute the probability of the coin to be fair.
    Means that this model uses both prior and posterior data.
    """

    @classmethod
    def expect_next_reward(cls, n_flips: int, n_heads: int) -> float:
        fairness = compute_fairness(n_flips, n_heads)
        next_head_prob = fairness * P_FAIR + (1 - fairness) * P_CHEAT
        return next_head_prob * expected_rewards[n_flips + 1][n_heads + 1] + \
               (1 - next_head_prob) * expected_rewards[n_flips + 1][n_heads]

    def end_condition(self, n_flips: int, n_heads: int) -> bool:
        return expected_rewards[n_flips][n_heads] > WeakBeliefModel.expect_next_reward(n_flips, n_heads)


class CalmBeliefModel(FanaticModel):
    """
    CalmBeliefModel

    Ends testing the coin if the reward is expected to be decreased; but if its for the first time, it keep testing.
    For computing next head probability, this model uses fairness to compute the probability of the coin to be fair.
    Means that this model uses both prior and posterior data.
    """

    def __init__(self, fund):
        super().__init__(fund)
        self.test_phase = 0

    def end_condition(self, n_flips: int, n_heads: int) -> bool:
        if expected_rewards[n_flips][n_heads] > BeliefModel.expect_next_reward(n_flips, n_heads) and \
                self.test_phase == 0:
            self.test_phase = 1
            return False

        if expected_rewards[n_flips][n_heads] > BeliefModel.expect_next_reward(n_flips, n_heads):
            return True

    def is_end_condition(self, coin: Coin) -> bool:
        if self.fund <= 0 or coin.n_flips >= R_if_correct - 1 or self.end_condition(coin.n_flips, coin.n_heads):
            self.test_phase = 0
            return True

        return False
