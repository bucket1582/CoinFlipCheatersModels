from compute_probabilities import *
from basic_models import AbstractModel, WeakBeliefModel, FanaticModel, BeliefModel
from collections import deque


class AbstractIndecisiveModel(AbstractModel):
    """
    An abstract model for indecisive models

    Indecisive models do not label the coins if fairness is not below significance level and 1 - fairness is also not
    below the significance level.
    """

    def __init__(self, fund: int, significance_level: float = 0.05):
        super().__init__(fund)
        self.significance_level = significance_level

    def is_significant(self, n_flips: int, n_heads: int) -> bool:
        fairness = compute_fairness(n_flips, n_heads)
        return fairness < self.significance_level or fairness > 1 - self.significance_level


class BasicIndecisiveModel(AbstractIndecisiveModel):
    """
    BasicIndecisiveModel

    Ends testing the coin if fairness or 1 - fairness is below significance level.
    """

    def end_condition(self, n_flips: int, n_heads: int) -> bool:
        fairness = compute_fairness(n_flips, n_heads)
        if self.is_significant(n_flips, n_heads):
            return True
        return False


class IndecisiveWeakBeliefModel(WeakBeliefModel, AbstractIndecisiveModel):
    """
    IndecisiveWeakBeliefModel

    Ends testing the coin if the reward is expected to be decreased.
    For computing next head probability, this model uses p_is_fair to compute the probability of the coin to be fair.

    For computing next expected reward, this model follows below logics
    i) if fairness(n, x) is significant -> the model label the coin
    thus if fairness(n + 1, x) or fairness(n + 1, x + 1) is significant -> the model expects itself to label the coin
    ii) otherwise -> the model keep testing
    thus if fairness(n + 1, x) and fairness(n + 1, x + 1) is not significant -> the model expects itself to keep on
    testing; i.e. the model would consider n + 2 cases either.
    """

    def expect_next_reward(self, n_flips: int, n_heads: int) -> float:
        next_head_prob = P_IS_FAIR * P_FAIR + (1 - P_IS_FAIR) * P_CHEAT

        # BFS
        expected_reward = 0
        q = deque([(n_flips, n_heads, 1)])
        while len(q) > 0:
            flips, heads, coefficient = q.popleft()
            if self.is_significant(flips, heads) or flips >= R_if_correct - 1:
                expected_reward += coefficient * expected_rewards[flips][heads]
            else:
                q.append((flips + 1, heads, coefficient * (1 - next_head_prob)))
                q.append((flips + 1, heads + 1, coefficient * next_head_prob))
        return expected_reward


class IndecisiveFanaticModel(WeakBeliefModel, AbstractIndecisiveModel):
    """
    IndecisiveFanaticModel

    Ends testing the coin if the reward is expected to be decreased.
    For computing next head probability, this model uses p_fair if the model considers current coin to more likely to
    be fair, and p_cheat otherwise.

    For computing next expected reward, this model follows below logics
    i) if fairness(n, x) is significant -> the model label the coin
    thus if fairness(n + 1, x) or fairness(n + 1, x + 1) is significant -> the model expects itself to label the coin
    ii) otherwise -> the model keep testing
    thus if fairness(n + 1, x) and fairness(n + 1, x + 1) is not significant -> the model expects itself to keep on
    testing; i.e. the model would consider n + 2 cases either.
    """

    def expect_next_reward(self, n_flips: int, n_heads: int) -> float:
        # BFS
        expected_reward = 0
        q = deque([(n_flips, n_heads, 1)])
        while len(q) > 0:
            flips, heads, coefficient = q.popleft()
            if self.is_significant(flips, heads) or flips >= R_if_correct - 1:
                expected_reward += coefficient * expected_rewards[flips][heads]
            else:
                if compute_fairness(flips, heads) > 0.5:
                    q.append((flips + 1, heads, coefficient * (1 - P_FAIR)))
                    q.append((flips + 1, heads + 1, coefficient * P_FAIR))
                else:
                    q.append((flips + 1, heads, coefficient * (1 - P_CHEAT)))
                    q.append((flips + 1, heads + 1, coefficient * P_CHEAT))
        return expected_reward


class IndecisiveBeliefModel(WeakBeliefModel, AbstractIndecisiveModel):
    """
    IndecisiveBeliefModel

    Ends testing the coin if the reward is expected to be decreased.
    For computing next head probability, this model uses fairness to compute the probability of the coin to be fair.

    For computing next expected reward, this model follows below logics
    i) if fairness(n, x) is significant -> the model label the coin
    thus if fairness(n + 1, x) or fairness(n + 1, x + 1) is significant -> the model expects itself to label the coin
    ii) otherwise -> the model keep testing
    thus if fairness(n + 1, x) and fairness(n + 1, x + 1) is not significant -> the model expects itself to keep on
    testing; i.e. the model would consider n + 2 cases either.
    """

    def expect_next_reward(self, n_flips: int, n_heads: int) -> float:
        # BFS
        expected_reward = 0
        q = deque([(n_flips, n_heads, 1)])
        while len(q) > 0:
            flips, heads, coefficient = q.popleft()
            if self.is_significant(flips, heads) or flips >= R_if_correct - 1:
                expected_reward += coefficient * expected_rewards[flips][heads]
            else:
                fairness = compute_fairness(n_flips, n_heads)
                next_head_prob = fairness * P_FAIR + (1 - fairness) * P_CHEAT
                q.append((flips + 1, heads, coefficient * (1 - next_head_prob)))
                q.append((flips + 1, heads + 1, coefficient * next_head_prob))
        return expected_reward
