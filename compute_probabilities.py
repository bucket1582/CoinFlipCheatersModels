# Probability for heads
P_FAIR = 0.5
P_CHEAT = 0.75

# Probability whether the coin is fair
P_IS_FAIR = 0.5

# Rewards
R_if_correct = 15
R_if_incorrect = -30

CHOOSE = [[0 for _ in range(R_if_correct + 1)] for _ in range(R_if_correct + 1)]
for n in range(1, R_if_correct + 1):
    for k in range(R_if_correct + 1):
        if k > n:
            CHOOSE[n][k] = 0
            continue

        if k == 0 or k == n:
            CHOOSE[n][k] = 1
            continue

        CHOOSE[n][k] = CHOOSE[n - 1][k - 1] + CHOOSE[n - 1][k]


def binomial(x: int, n: int, p: float) -> float:
    """
    Probability mass function for the binomial distribution

    :param x: Number of successes
    :param n: Number of trials
    :param p: Success probability
    :return: probability
    """
    global CHOOSE
    return CHOOSE[n][x] * pow(p, x) * pow(1 - p, n - x)


def compute_fairness(n_flips: int, n_heads: int) -> float:
    """
    Compute fairness; the probability of the coin to be fair.

    :param n_flips: Number of flips
    :param n_heads: Number of heads observed
    :return: fairness
    """
    # The probability of the coin to be fair; using bayes' theorem
    global P_FAIR, P_CHEAT, P_IS_FAIR
    if n_flips == 0:
        return P_IS_FAIR

    p_if_fair = binomial(n_heads, n_flips, P_FAIR)  # P(X = x|The coin is fair); X = # of heads
    p_if_cheat = binomial(n_heads, n_flips, P_CHEAT)  # P(X = x|The coin is not fair)
    p_fairness = p_if_fair * P_IS_FAIR
    p_cheatness = p_if_cheat * (1 - P_IS_FAIR)

    return p_fairness / (p_cheatness + p_fairness)


def compute_heads_probability(n_flips: int, n_heads: int, probability: float = P_IS_FAIR) -> float:
    """
    Compute the probability of heads; using total probability law

    :param n_flips: Number of flips
    :param n_heads: Number of heads observed
    :param probability: Probability of coin being fair
    :return: probability of getting head
    """
    global P_FAIR, P_CHEAT
    return probability * binomial(n_heads, n_flips, P_FAIR) + (1 - probability) * binomial(n_heads, n_flips, P_CHEAT)


def get_label_and_expected_reward(n_flips: int, n_heads: int) -> tuple[str, float]:
    """
    Return label and expected reward

    :param n_flips: Number of flips
    :param n_heads: Number of heads observed
    :return: two elements
    first element is FAIR if the coin is expected to be fair, otherwise CHEAT
    second element is the expected reward
    """
    fairness = compute_fairness(n_flips, n_heads)
    if fairness >= 0.5:
        # Consider the coin is fair
        return "FAIR", R_if_correct * fairness + R_if_incorrect * (1 - fairness) - n_flips
        # Subtract n_flips since n_flip is also a loss

    # Consider the coin is not fair
    return "CHEAT", R_if_incorrect * fairness + R_if_correct * (1 - fairness) - n_flips


expected_rewards = [[0.0 for _ in range(R_if_correct + 1)] for _ in range(R_if_correct + 1)]
labels = [["FAIR" for _ in range(R_if_correct + 1)] for _ in range(R_if_correct + 1)]
expected_rewards[0][0] = P_IS_FAIR * R_if_correct + (1 - P_IS_FAIR) * R_if_incorrect
labels[0][0] = "FAIR"
for num_flips in range(1, R_if_correct + 1):
    for num_heads in range(num_flips + 1):
        labels[num_flips][num_heads], expected_rewards[num_flips][num_heads] = get_label_and_expected_reward(num_flips,
                                                                                                             num_heads)

g_expected_rewards = [0.0 for _ in range(R_if_correct + 1)]
g_expected_rewards[0] = P_IS_FAIR * R_if_correct + (1 - P_IS_FAIR) * R_if_incorrect
for num_flips in range(1, R_if_correct + 1):
    mean_reward = 0
    for num_heads in range(num_flips + 1):
        mean_reward += expected_rewards[num_flips][num_heads] * compute_heads_probability(num_flips, num_heads)
    g_expected_rewards[num_flips] = mean_reward
