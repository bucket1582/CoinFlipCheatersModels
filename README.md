# CoinFlipCheatersModels
Made some models for the coin [flip cheaters](https://primerlearning.org/)

## Analysis
There are two types of coins in the problem.
1. fair coin (probability of heads is 1/2)
2. unfair coin (probability of heads is 3/4)

Using Bayes' theorem, one can find the probability of the coin to be fair. Let $n$ be the number of coin flips, $X$ be the number of heads, $p_{fair} = \dfrac{1}{2}$, $p_{cheat} = \dfrac{3}{4}$. One can easily say that $X \sim B(n, p_{fair})$ if the coin is fair, and $X \sim B(n, p_{cheat})$ otherwise.
