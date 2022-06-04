from coin import Coin
from fair_or_cheat_models import *

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
none_belief_model = NoBeliefModel(FUND)
weak_belief_model = WeakBeliefModel(FUND)
fanatic_model = FanaticModel(FUND)
sincere_fanatic_model = SincereFanaticModel(FUND)
calm_fanatic_model = CalmFanaticModel(FUND)

print(f"No belief model Result: {test_model(none_belief_model, 10000)}")
print(f"Weak belief Model Result: {test_model(weak_belief_model, 10000)}")
print(f"Fanatic model Result: {test_model(fanatic_model, 10000)}")
print(f"Sincere fanatic model Result: {test_model(sincere_fanatic_model, 10000)}")
print(f"Calm fanatic model Result: {test_model(calm_fanatic_model, 10000)}")
