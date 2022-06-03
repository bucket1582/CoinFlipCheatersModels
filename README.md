# CoinFlipCheatersModels
Made some models for the coin [flip cheaters](https://primerlearning.org/)

## Analysis
There are two types of coins in the problem.
1. fair coin (probability of heads is 1/2)
2. unfair coin (probability of heads is 3/4)

Using Bayes' theorem, one can find the probability of the coin to be fair. 

Let $n$ be the number of coin flips, $X$ be the number of heads, $p_{fair} = \dfrac{1}{2}$, $p_{cheat} = \dfrac{3}{4}$, and $p_{coin} = \dfrac{1}{2}$. Note that $p_{coin}$ means the probability of the coin to be fair without any observations. We can find that $X \sim B(n, p_{fair})$ if the coin is fair, and $X \sim B(n, p_{cheat})$ otherwise. Then, if $x$ of heads were observed from $n$ trials, by Bayes' theorem, we get

$$ fairness := P(\text{The coin is fair}|X = x) = \dfrac{b(x; n, p_{fair})p_{coin}}{b(x; n, p_{fair})p_{coin} + b(x; n, p_{cheat})(1 - p_{coin})} $$

where $b(x; n, p)$ is the probability mass function of the binomial distribution. Since $ P(\text{The coin is unfair}|X = x) = 1 - fairness$, if $fairness > \dfrac{1}{2}$, we can conclude that the coin is more likely to be fair. Otherwise, we may conclude that the coin is more likely to be unfair.

If we label right, we get 1 point and 15 flip chances. Otherwise we lose 30 flip chances. Consider only the flipping chances. If we flip once, we lose 1 flipping chance. Thus, we can evaluate the labeling process by below formula.

$$ reward := \begin{cases}
15 \ \ \ \ \ \text{if the label is correct} \\
-30 \ \ \ \ \ \text{o.w.}
\end{cases}$$

$$ \mathbb{E}[reward] = P(\text{the label is correct}) \times 15 + P(\text{the label is incorrect}) \times (-30) - n $$

For my model, I used $fairness$ for labeling. As mentioned above, if $fairness > 0.5$ the model label the coin as fair. Otherwise cheat. To calculate $fairness$ we need the number of flips, again $n$, and the number of heads, $x$. Therefore, the formula above can be written as below.

$$ \mathbb{E}[reward(n, x)] = \begin{cases}
fairness \times 15 + (1 - fairness) \times (-30) - n \ \ \ \ \ \text{if } fairness > 0.5 \\
(1 - fairness) \times 15 + fairness \times (-30) - n \ \ \ \ \ \text{o.w.}
\end{cases}
$$

From above, we can calculate the expected reward. If there is a way that maximizes the expected reward, we can take that as a strategy.

## Simple Model
The simple model tests a coin until the 'generally' expected reward is at its maximum. What I meant by the term generally is that it does not consider **how many times we got heads**.

$$ \mathbb{E}[reward(n)] = \Sigma_{x = 0}^{n} P(X = x) reward(n, x) $$

Suppose that $n = n^\*$ maximizes $reward(n)$. Then, the simple model flips the coin while $n < n^\*$, and finish testing if there is no flipping chance ramining, $n >= 14$, or $n >= n^\*$. The condition $n >= 14$ is naturally inducted from the fact that $reward <= 15$.

For $P(X = x)$, we use the law of total probability.

$$ \begin{align*} 
P(X = x) &= P(X = x \cap \text{The coin is fair}) + P(X = x \cap \text{The coin is unfair}) \\
&= p_{coin}b(x; n, p_{fair}) + (1 - p_{coin})b(x; n, p_{cheat}) 
\end{align*} $$

## Elastic Model
The elastic model tests a coin while the expected reward increases. Which means that we compare below two values.

1. $$ \mathbb{E}[reward(n, x)] $$
2. $$ P(\text{The next coin is head}) \times reward(n + 1, x + 1) + P(\text{The next coin is tail}) \times reward(n + 1, x) $$

If the first value is greater than the second value, the reward expected to be decreased, thus we label the coin instantly. Otherwise, the reward expected to be increased, thus we flip once more.

To calculate the second value, we use the law of total probability.

$$ \begin{align*} 
P(\text{The next coin is head}) &= P(\text{The coin is fair} \cap \text{The next coin is head}) + P(\text{The coin is unfair} \cap \text{The next coin is tail}) \\
&= p_{coin}p_{fair} + (1 - p_{coin})p_{cheat}
\end{align*} $$

We can calculate $P(\text{The next coin is tail})$ as $1 - P(\text{The next coin is head})$.

## Biased Model
The biased model is similar to the elastic model, except that it considers the 'current' label. As mentioned above, the coin can be labeled by using $fairness$. Because we have the number of flips and the number of heads, we can pre-label the coin as fair or cheat. We can use the pre-label to calculate the expected reward, instead of using the law of total probability. In formula,

$$ P(\text{The next coin is head}) = \begin{cases}
p_{fair} \ \ \ \ \ \text{if } fairness > 0.5 \text{ for } n, x \\
p_{cheat} \ \ \ \ \ \text{o.w.}
\end{cases} $$

