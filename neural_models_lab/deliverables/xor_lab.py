"""Neural models lab: XOR sensor-disagreement detector in PyTorch.

Runs every experiment in the lab and prints the results:
  Task 1  - linear (no hidden layer) baseline cannot learn XOR
  Task 4A - 2-2-1 network learns XOR (loss, probabilities, labels)
  Task 4B - gradients: autograd vs finite differences; mean loss = mean of per-example grads
  Task 4C - zero initialisation keeps hidden units identical
  Task 4D - sigmoid / tanh / ReLU comparison (+ success rate over 20 seeds)
  Task 5  - three-class extension with softmax + cross-entropy, p - y check
"""
import torch
import torch.nn as nn
import torch.nn.functional as F

torch.set_default_dtype(torch.float64)          # makes the finite-difference check precise
X = torch.tensor([[0., 0.], [0., 1.], [1., 0.], [1., 1.]])
Y = torch.tensor([[0.], [1.], [1.], [0.]])
ACTS = {"sigmoid": nn.Sigmoid, "tanh": nn.Tanh, "relu": nn.ReLU}
STEPS, LR = 5000, 0.1


def xor_net(act="tanh", hidden=2, out=1):
    return nn.Sequential(nn.Linear(2, hidden), ACTS[act](), nn.Linear(hidden, out))


def train(model, steps=STEPS, lr=LR, x=X, y=Y, loss_fn=nn.BCEWithLogitsLoss(), log_at=()):
    """Full-batch Adam. Returns (initial loss, final loss, {step: grad norm of W1})."""
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    grad_norms, first = {}, None
    for step in range(steps):
        opt.zero_grad()
        loss = loss_fn(model(x), y)             # forward pass + scalar loss
        loss.backward()                         # reverse-mode AD fills .grad
        if first is None:
            first = loss.item()
        if step in log_at:
            grad_norms[step] = model[0].weight.grad.norm().item()
        opt.step()                              # optimiser updates parameters
    with torch.no_grad():
        final = loss_fn(model(x), y).item()
    return first, final, grad_norms


def predictions(model):
    with torch.no_grad():
        p = torch.sigmoid(model(X)).squeeze(1)
    return p, (p > 0.5).long()


def task1():
    print("=== Task 1: linear model (affine + sigmoid, no hidden layer)")
    torch.manual_seed(0)
    model = nn.Sequential(nn.Linear(2, 1))
    first, final, _ = train(model)
    p, labels = predictions(model)
    print(f"initial loss {first:.4f}  final loss {final:.4f}  (ln 2 = 0.6931)")
    print("probabilities", [round(v, 3) for v in p.tolist()], "labels", labels.tolist())
    print(f"correct: {(labels == Y.squeeze(1).long()).sum().item()}/4\n")
    return final


def task4a():
    print("=== Task 4A: 2-2-1 tanh network, random init, seed 0")
    torch.manual_seed(0)
    model = xor_net("tanh")
    first, final, _ = train(model)
    p, labels = predictions(model)
    print(f"initial loss {first:.4f}  final loss {final:.6f}")
    for x, pi, li in zip(X.tolist(), p.tolist(), labels.tolist()):
        print(f"  x={x}  P(y=1)={pi:.4f}  label={li}")
    correct = (labels == Y.squeeze(1).long()).all().item()
    print("all four correct:", correct, "\n")
    return model, correct


def task4b():
    print("=== Task 4B: backpropagation check (fresh random net, seed 1)")
    torch.manual_seed(1)
    model = xor_net("tanh")
    loss_fn = nn.BCEWithLogitsLoss()
    model.zero_grad()
    loss_fn(model(X), Y).backward()
    W1 = model[0].weight
    autograd = W1.grad.clone()
    print("dL/dW1 (autograd):\n", autograd.numpy().round(6))

    # Finite-difference check of the same tensor: (L(w+h) - L(w-h)) / 2h
    fd, h = torch.zeros_like(W1), 1e-6
    with torch.no_grad():
        for i in range(W1.shape[0]):
            for j in range(W1.shape[1]):
                W1[i, j] += h; up = loss_fn(model(X), Y).item()
                W1[i, j] -= 2 * h; down = loss_fn(model(X), Y).item()
                W1[i, j] += h
                fd[i, j] = (up - down) / (2 * h)
    fd_err = (fd - autograd).abs().max().item()
    print(f"max |autograd - finite difference| = {fd_err:.2e}")

    # Mean loss -> gradient is the average of the per-example gradients
    per_example = []
    for k in range(4):
        model.zero_grad()
        loss_fn(model(X[k:k+1]), Y[k:k+1]).backward()
        per_example.append(W1.grad.clone())
    avg_err = (torch.stack(per_example).mean(0) - autograd).abs().max().item()
    print(f"max |mean of 4 per-example grads - batch grad| = {avg_err:.2e}\n")
    assert fd_err < 1e-6 and avg_err < 1e-12
    return autograd


def task4c():
    print("=== Task 4C: symmetry experiment (all weights and biases zero)")
    model = xor_net("tanh")
    for p in model.parameters():
        nn.init.zeros_(p)
    opt = torch.optim.SGD(model.parameters(), lr=0.5)
    loss_fn = nn.BCEWithLogitsLoss()
    for step in range(1001):
        opt.zero_grad()
        loss = loss_fn(model(X), Y)
        loss.backward()
        if step in (0, 1, 10, 100, 1000):
            W = model[0].weight.data
            print(f"step {step:4d} loss {loss.item():.4f}  W1 rows {W[0].tolist()} {W[1].tolist()}"
                  f"  identical={torch.equal(W[0], W[1])}  W1.grad={model[0].weight.grad.tolist()}")
        opt.step()

    # Same but with a nonzero, *identical* init: rows still stay identical.
    torch.manual_seed(0)
    model = xor_net("tanh")
    with torch.no_grad():
        model[0].weight[1] = model[0].weight[0]
        model[0].bias[1] = model[0].bias[0]
        model[2].weight[0, 1] = model[2].weight[0, 0]
    train(model, steps=2000)
    W = model[0].weight.data
    p, labels = predictions(model)
    print(f"identical nonzero init after 2000 Adam steps: rows identical={torch.allclose(W[0], W[1])}, "
          f"labels={labels.tolist()}\n")
    return torch.allclose(W[0], W[1])


def task4d():
    print("=== Task 4D: activation experiment (seed 0, same init seed for each)")
    print(f"{'activation':<10}{'final loss':>12}{'4/4?':>6}{'||grad W1|| @ step 10':>24}")
    rows = {}
    for name in ACTS:
        torch.manual_seed(0)
        model = xor_net(name)
        _, final, g = train(model, log_at=(0, 10))
        _, labels = predictions(model)
        ok = (labels == Y.squeeze(1).long()).all().item()
        rows[name] = (final, ok, g[10])
        print(f"{name:<10}{final:>12.5f}{str(ok):>6}{g[10]:>24.5f}")

    print("\nSuccess rate over 20 seeds (5000 Adam steps, lr 0.1):")
    for name in ACTS:
        wins = 0
        for seed in range(20):
            torch.manual_seed(seed)
            model = xor_net(name)
            train(model)
            wins += (predictions(model)[1] == Y.squeeze(1).long()).all().item()
        print(f"  {name:<8} {wins}/20")
    print()
    return rows


def task5():
    print("=== Task 5: three-class extension (softmax + cross-entropy)")
    y3 = torch.tensor([0, 1, 1, 2])
    torch.manual_seed(0)
    model = xor_net("tanh", hidden=2, out=3)
    print("final weight matrix shape:", tuple(model[2].weight.shape), " logits per example:", 3)
    first, final, _ = train(model, y=y3, loss_fn=nn.CrossEntropyLoss())
    with torch.no_grad():
        probs = F.softmax(model(X), dim=1)
    print(f"initial loss {first:.4f} (ln 3 = 1.0986)  final loss {final:.6f}")
    for x, p, t in zip(X.tolist(), probs.tolist(), y3.tolist()):
        print(f"  x={x}  p={[round(v, 4) for v in p]}  argmax={max(range(3), key=p.__getitem__)}  target={t}")
    acc = (probs.argmax(1) == y3).all().item()
    print("all four correct:", acc)
    print(f"sum of p for x=[0,1]: {probs[1].sum().item():.15f}")

    # Shift invariance: softmax(z + c) == softmax(z)
    z = model(X[1:2]).detach()
    shift_err = (F.softmax(z + 100, 1) - F.softmax(z, 1)).abs().max().item()
    print(f"max |softmax(z+100) - softmax(z)| = {shift_err:.2e}")
    naive = torch.exp(z.float() + 100) / torch.exp(z.float() + 100).sum()
    print(f"naive float32 exp(z+100) softmax -> {naive.tolist()} (overflow without max-subtraction)")

    # Logit gradient of mean cross-entropy is (p - y) / N
    z = model(X).detach().requires_grad_(True)
    F.cross_entropy(z, y3).backward()
    p_minus_y = (F.softmax(z, 1) - F.one_hot(y3, 3)) / 4
    pmy_err = (z.grad - p_minus_y).abs().max().item()
    print(f"max |dL/dz - (p - y)/N| = {pmy_err:.2e}\n")
    assert acc and shift_err < 1e-12 and pmy_err < 1e-12
    return acc


if __name__ == "__main__":
    lin = task1()
    _, ok = task4a()
    task4b()
    sym = task4c()
    task4d()
    task5()
    assert lin > 0.6 and ok and sym
    print("All checks passed.")
