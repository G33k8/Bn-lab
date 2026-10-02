# AI Laboratory: Bayesian Networks and Autoregressive Language Models

## 1. Objective

The objective of this laboratory is to connect Bayesian networks and conditional probability with autoregressive language modelling. The implementation constructs first-order and second-order models from a small text dataset, estimates conditional probability tables, predicts next words, generates text, and tests probabilistic invariants.

---

## 2. Dataset

The following six sentences were used:

1. the cat sat on the mat
2. the cat sat on the rug
3. the dog sat on the mat
4. the dog ran to the park
5. the cat ran to the park
6. the dog sat on the rug

Each sentence is converted to lowercase, tokenised by whitespace, and augmented with `<START>` and `<END>` tokens.

Example:

```text
<START> the cat sat on the mat <END>
```

---

# 3. Question 1

### Why is the chain-rule decomposition useful for generating text?

The chain rule decomposes the probability of a complete sequence into a sequence of conditional probabilities. This allows text to be generated one token at a time. At each step, the model estimates the probability of the next token given the preceding context, selects or samples a token, and then uses that token as context for the next prediction.

---

# 4. Question 2

### What independence assumption is being made by the first-order network?

The first-order model assumes that the next word depends only on the immediately preceding word:

\[
P(X_t \mid X_1,\ldots,X_{t-1})
\approx P(X_t\mid X_{t-1})
\]

Equivalently,

\[
X_t \perp \{X_1,\ldots,X_{t-2}\}\mid X_{t-1}.
\]

Thus, once the immediately preceding token is known, earlier tokens do not provide additional information according to the model.

---

# 5. Question 3

## Conditional probability distributions

The first-order model estimates:

\[
P(w_j\mid w_i)
=
\frac{C(w_i,w_j)}
{\sum_k C(w_i,w_k)}
\]

### `the`

| Next token | Count | Probability |
|---|---:|---:|
| cat | 3 | 0.2500 |
| dog | 3 | 0.2500 |
| mat | 2 | 0.1667 |
| rug | 2 | 0.1667 |
| park | 2 | 0.1667 |

### `cat`

| Next token | Count | Probability |
|---|---:|---:|
| sat | 2 | 0.6667 |
| ran | 1 | 0.3333 |

### `dog`

| Next token | Count | Probability |
|---|---:|---:|
| sat | 2 | 0.6667 |
| ran | 1 | 0.3333 |

### `sat`

| Next token | Count | Probability |
|---|---:|---:|
| on | 4 | 1.0000 |

### `ran`

| Next token | Count | Probability |
|---|---:|---:|
| to | 2 | 1.0000 |

Examples of zero-probability transitions include:

\[
P(dog\mid cat)=0
\]

\[
P(ran\mid sat)=0
\]

\[
P(cat\mid dog)=0
\]

\[
P(mat\mid cat)=0.
\]

Only transitions observed in the training corpus receive non-zero probability.

---

# 6. Question 4

### Where are the transition counts stored?

The implementation stores transition counts in:

```python
transition_counts[current][next]
```

For example:

```python
transition_counts["cat"]["sat"] = 2
```

This means that `sat` occurred twice immediately after `cat`.

---

# 7. Question 5

### Where is P(X_t | X_{t-1}) computed?

The conditional probability is calculated by dividing each transition count by the total number of observed transitions from the conditioning word:

```python
total = sum(next_counts.values())

probability = count / total
```

Mathematically:

\[
P(w_j\mid w_i)
=
\frac{C(w_i,w_j)}
{\sum_k C(w_i,w_k)}.
\]

---

# 8. Question 6

### How does the program choose the next word?

The implementation supports both deterministic greedy selection and probabilistic sampling.

Greedy generation chooses:

\[
\arg\max_w P(w\mid w_{\text{previous}})
\]

Sampling instead draws a word according to the conditional probability distribution.

For example:

```text
P(sat | cat) = 0.6667
P(ran | cat) = 0.3333
```

Greedy generation always chooses `sat`, whereas sampling can choose either `sat` or `ran`, with `sat` being approximately twice as likely.

---

# 9. Question 7

### What happens if no transition has been observed?

If the current word has no observed outgoing transition, the distribution is empty and the implementation returns `None`. Generation then stops.

This is a limitation of the unsmoothed count-based model: an unseen transition has probability zero.

---

# 10. Question 8

### What does a normalization total of 0.87 mean?

For every context \(w\), the conditional probability distribution must satisfy:

\[
\sum_v P(v\mid w)=1.
\]

Therefore, a total of 0.87 indicates that the probability distribution has not been constructed correctly. Possible causes include incorrect counting, an incorrect normalization denominator, missing probability entries, or another implementation error.

The normalization test is therefore an important correctness check.

---

# 11. Question 9

### Are the most probable predictions always what a human would expect?

No. The model only represents statistical relationships observed in the training data. It does not possess the broad linguistic knowledge or semantic understanding of a human.

For example:

```text
P(sat | cat) = 0.6667
P(ran | cat) = 0.3333
```

These probabilities are determined by the frequency of the two transitions in the dataset. The model therefore reflects the training corpus rather than general human linguistic expectations.

---

# 12. Generated Text

The program generates at least 20 sentences using probabilistic sampling.

The actual generated output is included in the execution-output section at the end of this report. A fixed random seed of 42 is used so that the experiment is reproducible.

---

# 13. Question 10

### Greedy versus sampling generation

Greedy generation always selects the highest-probability next token. Consequently, it tends to repeatedly produce the same sentence or sequence of high-probability transitions.

Sampling instead follows the probability distribution and can select lower-probability transitions. Therefore, sampling produces greater variation.

For example, after `cat`:

\[
P(sat\mid cat)=0.6667
\]

and

\[
P(ran\mid cat)=0.3333.
\]

Greedy generation always selects `sat`, while sampling can select either word.

---

# 14. Second-Order Bayesian Network

The second-order model estimates:

\[
P(X_t\mid X_{t-2},X_{t-1}).
\]

It therefore uses two previous tokens as context instead of one.

---

# 15. Question 11

### Difference between first-order and second-order models

#### 1. Graph structure

The first-order model uses:

\[
X_{t-1}\rightarrow X_t.
\]

The second-order model uses:

\[
X_{t-2}\rightarrow X_t
\]

and

\[
X_{t-1}\rightarrow X_t.
\]

#### 2. Conditional probability table

First-order:

\[
P(X_t\mid X_{t-1}).
\]

Second-order:

\[
P(X_t\mid X_{t-2},X_{t-1}).
\]

The second-order CPT is therefore indexed by pairs of previous tokens.

#### 3. Context

The first-order model uses one previous token. The second-order model uses two previous tokens.

#### 4. Data requirements

The second-order model requires more data because it must estimate probabilities for combinations of two previous tokens. Consequently, its CPT is more sparse when training data is limited.

---

# 16. Second-Order CPT

Selected contexts include:

| Context | Next token | Probability |
|---|---|---:|
| `<START>, the` | cat | 0.5000 |
| `<START>, the` | dog | 0.5000 |
| `the, cat` | sat | 0.6667 |
| `the, cat` | ran | 0.3333 |
| `the, dog` | sat | 0.6667 |
| `the, dog` | ran | 0.3333 |
| `cat, sat` | on | 1.0000 |
| `sat, on` | the | 1.0000 |
| `on, the` | mat | 0.5000 |
| `on, the` | rug | 0.5000 |
| `dog, ran` | to | 1.0000 |
| `ran, to` | the | 1.0000 |
| `to, the` | park | 1.0000 |
| `cat, ran` | to | 1.0000 |

---

# 17. Question 12

### Why can additional context improve prediction but make estimation harder?

Additional context can provide more information about the next token. A second-order model can distinguish contexts that have the same most recent word but different words before it.

However, the number of possible contexts increases rapidly.

For a vocabulary of size \(V\):

- first-order contexts are approximately \(V\);
- second-order contexts are approximately \(V^2\);
- third-order contexts are approximately \(V^3\).

Thus, increasing context size makes the conditional probability table larger and increases the amount of data required to estimate it reliably.

With limited training data, many contexts remain unobserved, producing zero-probability contexts.

---

# 18. First-Order versus Second-Order Comparison

The vocabulary contains 12 tokens when `<START>` and `<END>` are included.

The first-order model has:

- 11 observed conditioning contexts;
- 17 observed probability entries.

The second-order model has:

- 14 observed two-token contexts;
- 18 observed probability entries.

For the zero-context comparison, all possible vocabulary contexts are considered:

- first-order: \(12\) possible contexts, with \(11\) observed;
- second-order: \(12^2=144\) possible contexts, with \(14\) observed.

Therefore:

```text
First-order zero contexts: 1
Second-order zero contexts: 130
```

This definition treats every possible vocabulary word/pair as a possible context. The large increase in unobserved second-order contexts demonstrates the data-sparsity problem.

Qualitatively, the second-order model has more contextual information but requires more observations to estimate its larger conditional table reliably.

---

# 19. Question 13

### Why is a specific probabilistic specification preferable when using an LLM?

A specific probabilistic specification is preferable because it defines the intended behaviour before implementation begins.

The developer should specify:

- what the variables represent;
- which variables depend on which others;
- which probability distribution is being estimated;
- how the probabilities are calculated;
- how generation should work;
- what properties the implementation must satisfy.

For this laboratory, specifying

\[
P(X_t\mid X_{t-1})
\]

and transition-count estimation gives an objective target against which the generated code can be evaluated.

Validation is particularly important when using an LLM because syntactically correct code can still implement the wrong probabilistic model.

The normalization invariant

\[
\sum_v P(v\mid w)=1
\]

provides a simple test of whether the conditional distributions were constructed correctly.

The implementation and the model should therefore be treated as separate concepts: the LLM can help construct the implementation, while the developer remains responsible for specifying and validating the probabilistic model.

---

# 20. Question 14

### What does the Bayesian-network perspective add?

Thinking of the language model as a Bayesian network provides several useful perspectives.

First, it gives an explicit representation of dependencies between tokens.

Second, it gives a factorisation of the joint probability distribution. For the first-order model:

\[
P(X_1,\ldots,X_T)
=
P(X_1)
\prod_{t=2}^{T}P(X_t\mid X_{t-1}).
\]

Third, the CPT entries have a direct interpretation as conditional probabilities.

Fourth, the model provides a principled generation procedure: repeatedly sample the next token from its conditional distribution.

Fifth, the Bayesian-network representation makes independence assumptions explicit.

Finally, changing from first-order to second-order structure makes it clear how increasing context changes the conditional distribution and increases the number of parameters that need to be estimated.

---

# 21. Probability Normalization Results

The implementation checks:

\[
\sum_v P(v\mid context)=1.
\]

For every observed first-order and second-order context, the result should be:

```text
1.0000000000 -> PASS
```

The test is included directly in `bn_language_model.py`.

---

# 22. LLM Reflection

An LLM was used to assist with implementing the probabilistic models. The model was given a behavioural specification rather than simply being asked to write a generic language model.

The implementation was then inspected against the mathematical specification.

One concrete validation was checking the transition-count representation. The first-order implementation stores counts as:

```python
transition_counts[current][next]
```

For example:

```python
transition_counts["cat"]["sat"] = 2
```

The probability calculation was then checked against the mathematical definition:

\[
P(w_j\mid w_i)
=
\frac{C(w_i,w_j)}
{\sum_k C(w_i,w_k)}.
\]

I also added normalization tests to verify that every conditional distribution sums to one.

For the second-order model, I verified that the conditioning context consists of two previous tokens:

```python
context = (sentence[i - 2], sentence[i - 1])
```

rather than accidentally retaining the first-order model's single-token context.

Finally, the generated output was inspected to confirm that greedy generation is deterministic while sampling can produce different sentences. This validation separates correctness of the implementation from merely obtaining executable Python code.

---

# 23. Conclusion

The laboratory demonstrates the progression:

\[
\text{Probability}
\rightarrow
\text{Bayesian Network}
\rightarrow
\text{Autoregressive Model}
\rightarrow
\text{Language Generation}.
\]

The simple n-gram models used here are not comparable in expressive power to modern neural language models. However, they share the same central probabilistic idea:

\[
P(\text{next token}\mid\text{previous tokens}).
\]

The primary difference is how the conditional distribution is represented and learned.

---

# 24. Reproducibility

Run:

```bash
python3 bn_language_model.py
```

The program uses:

```python
random.seed(42)
```

so the sampling experiment is reproducible.

---

# 25. Execution Output

The following is the reproducible output from running `python3 bn_language_model.py` with random seed 42.

```text
======================================================================
FIRST-ORDER CPT
======================================================================

<START>
  P(the) = 1.0000

cat
  P(ran) = 0.3333
  P(sat) = 0.6667

dog
  P(ran) = 0.3333
  P(sat) = 0.6667

mat
  P(<END>) = 1.0000

on
  P(the) = 1.0000

park
  P(<END>) = 1.0000

ran
  P(to) = 1.0000

rug
  P(<END>) = 1.0000

sat
  P(on) = 1.0000

the
  P(cat) = 0.2500
  P(dog) = 0.2500
  P(mat) = 0.1667
  P(park) = 0.1667
  P(rug) = 0.1667

to
  P(the) = 1.0000

======================================================================
FIRST-ORDER NORMALIZATION
======================================================================
<START>    -> 1.0000000000 -> PASS
the        -> 1.0000000000 -> PASS
cat        -> 1.0000000000 -> PASS
sat        -> 1.0000000000 -> PASS
on         -> 1.0000000000 -> PASS
mat        -> 1.0000000000 -> PASS
rug        -> 1.0000000000 -> PASS
dog        -> 1.0000000000 -> PASS
ran        -> 1.0000000000 -> PASS
to         -> 1.0000000000 -> PASS
park       -> 1.0000000000 -> PASS

======================================================================
NEXT-WORD PREDICTIONS
======================================================================
<START>    -> the
             {'the': 1.0}
the        -> cat
             {'cat': 0.25, 'mat': 0.16666666666666666, 'rug': 0.16666666666666666, 'dog': 0.25, 'park': 0.16666666666666666}
cat        -> sat
             {'sat': 0.6666666666666666, 'ran': 0.3333333333333333}
dog        -> sat
             {'sat': 0.6666666666666666, 'ran': 0.3333333333333333}
sat        -> on
             {'on': 1.0}
ran        -> to
             {'to': 1.0}

======================================================================
20 FIRST-ORDER SAMPLED SENTENCES
======================================================================
 1. the cat sat on the dog ran to the cat sat on the cat sat on the dog ran to the dog sat on the mat
 2. the park
 3. the dog sat on the rug
 4. the park
 5. the cat sat on the cat sat on the mat
 6. the mat
 7. the dog sat on the mat
 8. the rug
 9. the dog sat on the mat
10. the park
11. the mat
12. the mat
13. the mat
14. the mat
15. the rug
16. the cat sat on the cat sat on the park
17. the dog ran to the dog sat on the park
18. the rug
19. the park
20. the dog sat on the dog sat on the cat ran to the mat

======================================================================
5 FIRST-ORDER GREEDY SENTENCES
======================================================================
1. the cat sat on the cat sat on the cat sat on the cat sat on the cat sat on the cat sat on the cat sat on the cat
2. the cat sat on the cat sat on the cat sat on the cat sat on the cat sat on the cat sat on the cat sat on the cat
3. the cat sat on the cat sat on the cat sat on the cat sat on the cat sat on the cat sat on the cat sat on the cat
4. the cat sat on the cat sat on the cat sat on the cat sat on the cat sat on the cat sat on the cat sat on the cat
5. the cat sat on the cat sat on the cat sat on the cat sat on the cat sat on the cat sat on the cat sat on the cat

======================================================================
5 FIRST-ORDER SAMPLED SENTENCES
======================================================================
1. the park
2. the cat ran to the rug
3. the park
4. the rug
5. the mat

======================================================================
SECOND-ORDER CPT
======================================================================

('<START>', 'the')
  P(cat) = 0.5000
  P(dog) = 0.5000

('cat', 'ran')
  P(to) = 1.0000

('cat', 'sat')
  P(on) = 1.0000

('dog', 'ran')
  P(to) = 1.0000

('dog', 'sat')
  P(on) = 1.0000

('on', 'the')
  P(mat) = 0.5000
  P(rug) = 0.5000

('ran', 'to')
  P(the) = 1.0000

('sat', 'on')
  P(the) = 1.0000

('the', 'cat')
  P(ran) = 0.3333
  P(sat) = 0.6667

('the', 'dog')
  P(ran) = 0.3333
  P(sat) = 0.6667

('the', 'mat')
  P(<END>) = 1.0000

('the', 'park')
  P(<END>) = 1.0000

('the', 'rug')
  P(<END>) = 1.0000

('to', 'the')
  P(park) = 1.0000

======================================================================
SECOND-ORDER NORMALIZATION
======================================================================
('<START>', 'the')        -> 1.0000000000 -> PASS
('the', 'cat')            -> 1.0000000000 -> PASS
('cat', 'sat')            -> 1.0000000000 -> PASS
('sat', 'on')             -> 1.0000000000 -> PASS
('on', 'the')             -> 1.0000000000 -> PASS
('the', 'mat')            -> 1.0000000000 -> PASS
('the', 'rug')            -> 1.0000000000 -> PASS
('the', 'dog')            -> 1.0000000000 -> PASS
('dog', 'sat')            -> 1.0000000000 -> PASS
('dog', 'ran')            -> 1.0000000000 -> PASS
('ran', 'to')             -> 1.0000000000 -> PASS
('to', 'the')             -> 1.0000000000 -> PASS
('the', 'park')           -> 1.0000000000 -> PASS
('cat', 'ran')            -> 1.0000000000 -> PASS

======================================================================
5 SECOND-ORDER GREEDY SENTENCES
======================================================================
1. the cat sat on the mat
2. the cat sat on the mat
3. the cat sat on the mat
4. the cat sat on the mat
5. the cat sat on the mat

======================================================================
5 SECOND-ORDER SAMPLED SENTENCES
======================================================================
1. the cat sat on the mat
2. the cat sat on the rug
3. the cat ran to the park
4. the dog ran to the park
5. the dog ran to the park

======================================================================
MODEL COMPARISON
======================================================================
Vocabulary size: 12
First-order observed probability entries: 17
Second-order observed probability entries: 18
First-order zero-probability contexts: 1
Second-order zero-probability contexts: 130
```
