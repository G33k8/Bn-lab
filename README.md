# AI Labs

Each lab is in `<lab>/deliverables/`, which holds the code, the captured output, a report answering every question in the lab sheet, and the LLM prompts used.

| Folder | Lab | Run |
|---|---|---|
| `agents_lab/` | Goal-based warehouse agent (BFS) | `python3 warehouse_agent.py` |
| `search_lab/` | A* vs BFS, heuristic experiments | `python3 search_agent.py` |
| `logic_lab/` | STRIPS planner + Prolog verifier | `python3 planner.py`, `swipl -q -s planner.pl -g run_queries -t halt` |
| `bn_lab/` | Bayesian networks / n-gram language models | `python3 bn_language_model.py` |
| `neural_models_lab/` | XOR in PyTorch, activations, softmax | `python xor_lab.py` (needs `torch`) |
