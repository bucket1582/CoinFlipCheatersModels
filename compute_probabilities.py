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


def binomial(x, n, p):
    global CHOOSE
    return CHOOSE[n][x] * pow(p, x) * pow(1 - p, n - x)


def compute_fairness(n_flips, n_heads):
    # The probability of the coin to be fair; using bayes' theorem
    global P_FAIR, P_CHEAT, P_IS_FAIR
    p_if_fair = binomial(n_heads, n_flips, P_FAIR)  # P(X = x|The coin is fair); X = # of heads
    p_if_cheat = binomial(n_heads, n_flips, P_CHEAT)  # P(X = x|The coin is not fair)
    p_fairness = p_if_fair * P_IS_FAIR
    p_cheatness = p_if_cheat * (1 - P_IS_FAIR)

    return  p_fairness / (p_cheatness + p_fairness)


def compute_heads(n_flips, n_heads):
    # Compute the probability of heads; using total probability law
    global P_FAIR, P_CHEAT, P_IS_FAIR
    return P_IS_FAIR * binomial(n_heads, n_flips, P_FAIR) + (1 - P_IS_FAIR) * binomial(n_heads, n_flips, P_CHEAT)


def expected_reward(n_flips, n_heads):
    fairness = compute_fairness(n_flips, n_heads)
    if fairness >= 0.5:
        # Consider the coin is fair
        return "FAIR", R_if_correct * fairness + R_if_incorrect * (1 - fairness) - n_flips
        # Subtract n_flips since n_flip is also a loss

    # Consider the coin is not fair
    return "CHEAT", R_if_incorrect * fairness + R_if_correct * (1 - fairness) - n_flips


rewards = [[("", 0.0) for _ in range(R_if_correct + 1)] for _ in range(R_if_correct + 1)]
rewards[0][0] = ("FAIR", P_IS_FAIR * R_if_correct + (1 - P_IS_FAIR) * R_if_incorrect)
for num_flips in range(1, R_if_correct + 1):
    for num_heads in range(num_flips + 1):
        rewards[num_flips][num_heads] = expected_reward(num_flips, num_heads)

expected_rewards = [0.0 for _ in range(R_if_correct + 1)]
expected_rewards[0] = P_IS_FAIR * R_if_correct + (1 - P_IS_FAIR) * R_if_incorrect
for num_flips in range(1, R_if_correct + 1):
    mean_reward = 0
    for num_heads in range(num_flips + 1):
        mean_reward += rewards[num_flips][num_heads][1] * compute_heads(num_flips, num_heads)
    expected_rewards[num_flips] = mean_reward


def get_reward(n_flips, n_heads):
    global rewards
    return rewards[n_flips][n_heads]


def get_general_expected_rewards(n_flips):
    global expected_rewards
    return expected_rewards[n_flips]


def get_local_expected_rewards(n_flips, n_heads):
    # If I get n_heads out of n_flips, should I test once more?
    # What is the expected reward after one more test?
    global rewards, P_IS_FAIR, P_FAIR, P_CHEAT
    next_head_prob = P_IS_FAIR * P_FAIR + (1 - P_IS_FAIR) * P_CHEAT
    return next_head_prob * rewards[n_flips + 1][n_heads + 1][1] + (1 - next_head_prob) * rewards[n_flips + 1][n_heads][1]


def get_local_expected_rewards_with_prior(n_flips, n_heads):
    # Compute expected reward using current decision
    global rewards, P_IS_FAIR, P_FAIR, P_CHEAT
    if rewards[n_flips][n_heads][0] == "FAIR":
        return P_FAIR * rewards[n_flips + 1][n_heads + 1][1] + (1 - P_FAIR) * rewards[n_flips + 1][n_heads][1]

    return P_CHEAT * rewards[n_flips + 1][n_heads + 1][1] + (1 - P_CHEAT) * rewards[n_flips + 1][n_heads][1]
