# LLM Prompts: Neural Models Lab

LLM used: Claude (Anthropic).

## Prompt 1 (Task 3)
> Generate minimal PyTorch code for the following model and dataset. Do not change the architecture or task. Dataset: XOR with inputs (0,0),(0,1),(1,0),(1,1) and labels 0,1,1,0. Model: 2–2–1, tanh hidden layer, one output logit trained with BCEWithLogitsLoss, random init, full-batch training for 5000 steps on CPU. After training, report the final loss, all four probabilities, thresholded labels, and one parameter-gradient tensor. Set a random seed for reproducibility and explain each test in one sentence.

## Prompt 2 (Task 4)
> Add: a finite-difference check of dL/dW1; a copy of the experiment with all weights zero, printing the hidden weight rows over several steps; and a loop over sigmoid/tanh/ReLU that records final loss, 4/4 correctness and the first-layer gradient norm at step 10.

## Prompt 3 (Task 5)
> Modify only the output/loss portion: 3 logits, CrossEntropyLoss, targets 0/1/1/2. Print softmax probabilities, check they sum to 1, check shift invariance under +100, and compare dL/dz to (p − y)/N.

## Changes I made
- Switched to float64 so the finite-difference check is meaningful.
- Added the identical-but-nonzero init case to Task 4C (zero init alone also has zero gradients, which hides the symmetry argument).
- Added the 20-seed success-rate sweep after noticing that a single run overstates reliability.
