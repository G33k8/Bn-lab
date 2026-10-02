# Neural Models Lab: XOR, Depth, Activations, Output Layers

**Files:** `xor_lab.py` (all experiments, with assertions), `output.txt` (its full output), `prompts.md`.
Run: `pip install torch` then `python xor_lab.py` (CPU, about 1.5 min, most of it the 20-seed sweep).

## Task 1: Problem specification
- X = {0,1}², Y = {0,1}. Examples: (0,0)→0, (0,1)→1, (1,0)→1, (1,1)→0.
- In the plane, the class-1 points (0,1) and (1,0) lie on one diagonal and the class-0 points (0,0) and (1,1) on the other. A single line cannot put both diagonals on opposite sides: the four inequalities w·x+b would need are contradictory (b<0, w1+b>0, w2+b>0, w1+w2+b<0).
- **Prediction:** affine + sigmoid will settle at p = 0.5 for every input, with loss ln 2.
- **Observed:** final loss 0.6931 = ln 2, all probabilities 0.5, 2/4 correct.

## Task 2: Design and validation criteria
2–2–1 network, tanh hidden layer (sigmoid and ReLU also tried), one logit trained with `BCEWithLogitsLoss` (sigmoid + BCE, numerically stable), full-batch Adam, lr 0.1, 5000 steps.
1. The hidden nonlinearity is necessary because stacked affine layers collapse into one affine map, which Task 1 shows cannot represent XOR.
2. Sigmoid + BCE is the Bernoulli negative log-likelihood. Its logit gradient is p − y, which doesn't vanish when the output saturates on the wrong side.
3. Success checks: final loss ≪ ln 2; 4/4 thresholded labels correct; nonzero first-layer gradient that matches finite differences; behaviour over many seeds.

**Think about it:** the hidden units have no targets. Backpropagation assigns each one a share of the output error, ∂L/∂h, and that signal is what shapes them into features (e.g. OR-like and AND-like units).

## Task 4: Results
**A. Learning (tanh, seed 0):** loss 0.7102 → 0.000012. Probabilities 0.0000 / 1.0000 / 1.0000 / 0.0000, all 4 correct.

**B. Backprop:** `W1.grad` holds ∂L/∂W⁽¹⁾, the change in the scalar loss per unit change of each first-layer weight. Autograd agrees with central finite differences to 4e-11. The loss is the *mean* over the 4 examples and differentiation is linear, so the batch gradient equals the average of the per-example gradients (difference 7e-18, verified).

**C. Symmetry:** with every parameter zero, tanh(0) = 0. Both hidden outputs are 0, so the output weights get zero gradient, and since the output weights are 0, so do the hidden weights. W1 stays exactly zero and the loss stays at ln 2 for 1000 steps. With an *identical nonzero* initialisation the two rows still stay identical after 2000 Adam steps, and the net only gets 3/4 right: identical units compute the same thing, receive the same gradient and so remain copies. The network effectively has one hidden unit.

**D. Activations (same seed 0 init):**

| Hidden activation | Final loss | 4/4 correct? | ‖∇W⁽¹⁾L‖₂ at step 10 |
|---|---|---|---|
| Sigmoid | 0.00003 | yes | 0.0024 |
| Tanh | 0.00001 | yes | 0.0374 |
| ReLU | 0.00001 | yes | 0.0416 |

Success over 20 seeds: sigmoid 7/20, tanh 8/20, ReLU 8/20. With lr 0.01 the results are similar (8, 9, 7 out of 20), so the learning rate is not the cause. The failed runs end at loss ≈ 0.347 (= ln2/2) or 0.477 with 2–3/4 correct, which are the known local minima of the minimal 2–2–1 XOR network. Failed ReLU runs also sit at 0.693 (dead units, zero gradient).
Interpretation: the sigmoid gradient is about 15× smaller early on because σ′ ≤ 0.25 while tanh′ ≤ 1 and active ReLU′ = 1. All three can solve XOR from a good initialisation. With only 2 hidden units, the initialisation matters more than the choice of activation. These four data points don't show that any one activation is generally best.

## Task 5: Three-class extension
Predicted before running: final weight matrix 3×2, 3 logits per example. Softmax sums to 1 because each exp is divided by the sum of all of them. The logit gradient of CE is p − y because ∂/∂z_k [−z_y + log Σexp z] = softmax_k − 1[k=y].
Results: loss 1.024 → 3e-6. p(0,0) = [1,0,0], p(0,1) = p(1,0) = [0,1,0], p(1,1) = [0,0,1], 4/4 correct. Σp for (0,1) = 1.000000000000000. Adding 100 to all logits changes the probabilities by 9e-21, but a naive float32 exp(z+100) overflows to NaN. That is why stable implementations subtract the max logit. Autograd's dL/dz matches (p − y)/N to 4e-22.

## Reflection
1. **Depth vs nonlinearity:** depth alone (affine layers) gives nothing new. It is the nonlinearity that lets a hidden layer re-represent the inputs so that XOR becomes linearly separable.
2. **Evidence of a useful learning signal:** the loss fell by five orders of magnitude, all labels became correct, and the gradient matched finite differences. A merely nonzero gradient would not have done that (the zero-init run never moved off ln 2).
3. **Zero init:** identical units get identical gradients, so the symmetry is never broken (Task 4C).
4. **Activation effect:** observed: sigmoid has the smallest early gradient norm. Scientific explanation: σ′ ≤ 0.25 compounds through the chain rule, tanh′ is up to 1, and ReLU′ is 0 or 1. Sigmoid saturation and dead ReLUs (pre-activation < 0) can be told apart by looking at the pre-activations: large |a| for sigmoid, a < 0 for ReLU.
5. **Output and loss together:** the output nonlinearity defines the probability model and the loss is its negative log-likelihood. Matching them (sigmoid + BCE, softmax + CE) gives the clean p − y gradient. Mismatches (e.g. sigmoid + MSE) give vanishing gradients or the wrong semantics.
6. **LLM:** a productivity win was generating the training loop and the finite-difference check in seconds. Verification was essential for the 20-seed sweep: a single seed-0 run suggested XOR is "always learned", and the true rate is about 40%.
7. **What scales:** I would keep the loss curves, label/accuracy checks, softmax-sum and shift checks, the symmetry check and spot gradient checks. Exhaustive finite differences (2 forward passes per parameter) and many-seed sweeps become too expensive.
