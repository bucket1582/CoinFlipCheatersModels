from compute_probabilities import *

max_general_expected_rewards = None
max_general_expected_rewards_idx = 0
for n in range(len(expected_rewards)):
    if max_general_expected_rewards is None or expected_rewards[n] > max_general_expected_rewards:
        max_general_expected_rewards = expected_rewards[n]
        max_general_expected_rewards_idx = n


def simple_feed(n_flips, n_heads):
    if n_flips < R_if_correct - 1 and n_flips < max_general_expected_rewards_idx:
        return "CONTINUE"

    return get_reward(n_flips, n_heads)[0]


def elastic_feed(n_flips, n_heads):
    if n_flips < R_if_correct - 1 and \
            rewards[n_flips][n_heads][1] <= get_local_expected_rewards(n_flips, n_heads):
        return "CONTINUE"

    return get_reward(n_flips, n_heads)[0]


def biased_feed(n_flips, n_heads):
    if n_flips < R_if_correct - 1 and \
            rewards[n_flips][n_heads][1] <= get_local_expected_rewards_with_prior(n_flips, n_heads):
        return "CONTINUE"

    return get_reward(n_flips, n_heads)[0]


def build_cheat_sheet_simple():
    cheat_sheet = [["X" for _ in range(R_if_correct + 1)] for _ in range(R_if_correct + 1)]
    for num_flips in range(R_if_correct + 1):
        for num_heads in range(num_flips + 1):
            cheat_sheet[num_flips][num_heads] = simple_feed(num_flips, num_heads)
    return cheat_sheet


def build_cheat_sheet_elastic():
    cheat_sheet = [["X" for _ in range(R_if_correct + 1)] for _ in range(R_if_correct + 1)]
    for num_flips in range(R_if_correct + 1):
        for num_heads in range(num_flips + 1):
            cheat_sheet[num_flips][num_heads] = elastic_feed(num_flips, num_heads)
    return cheat_sheet


def build_cheat_sheet_biased():
    cheat_sheet = [["X" for _ in range(R_if_correct + 1)] for _ in range(R_if_correct + 1)]
    for num_flips in range(R_if_correct + 1):
        for num_heads in range(num_flips + 1):
            cheat_sheet[num_flips][num_heads] = biased_feed(num_flips, num_heads)
    return cheat_sheet


biased_cheat_sheet = build_cheat_sheet_biased()
for row in biased_cheat_sheet:
    print(row)
