from collections import Counter, defaultdict
import random

START = "<START>"
END = "<END>"

SENTENCES = [
    "the cat sat on the mat",
    "the cat sat on the rug",
    "the dog sat on the mat",
    "the dog ran to the park",
    "the cat ran to the park",
    "the dog sat on the rug",
]


def tokenize_sentences(sentences):
    return [[START] + s.lower().strip().split() + [END] for s in sentences]


class FirstOrderLanguageModel:
    """P(X_t | X_{t-1})"""

    def __init__(self):
        self.transition_counts = defaultdict(Counter)
        self.probabilities = defaultdict(dict)

    def train(self, tokenized_sentences):
        for sentence in tokenized_sentences:
            for i in range(len(sentence) - 1):
                current = sentence[i]
                nxt = sentence[i + 1]
                self.transition_counts[current][nxt] += 1
        self._calculate_probabilities()

    def _calculate_probabilities(self):
        for current, next_counts in self.transition_counts.items():
            total = sum(next_counts.values())
            self.probabilities[current] = {
                nxt: count / total
                for nxt, count in next_counts.items()
            }

    def get_distribution(self, current):
        return self.probabilities.get(current, {})

    def predict_next(self, current):
        distribution = self.get_distribution(current)
        if not distribution:
            return None
        return max(distribution, key=distribution.get)

    def sample_next(self, current):
        distribution = self.get_distribution(current)
        if not distribution:
            return None
        words = list(distribution)
        weights = list(distribution.values())
        return random.choices(words, weights=weights, k=1)[0]

    def generate_greedy(self, max_length=30):
        current = START
        output = []

        for _ in range(max_length):
            nxt = self.predict_next(current)
            if nxt is None or nxt == END:
                break
            output.append(nxt)
            current = nxt

        return " ".join(output)

    def generate_sample(self, max_length=30):
        current = START
        output = []

        for _ in range(max_length):
            nxt = self.sample_next(current)
            if nxt is None or nxt == END:
                break
            output.append(nxt)
            current = nxt

        return " ".join(output)

    def check_normalization(self, tolerance=1e-9):
        results = {}
        for context, distribution in self.probabilities.items():
            total = sum(distribution.values())
            results[context] = (total, abs(total - 1.0) <= tolerance)
        return results


class SecondOrderLanguageModel:
    """P(X_t | X_{t-2}, X_{t-1})"""

    def __init__(self):
        self.transition_counts = defaultdict(Counter)
        self.probabilities = defaultdict(dict)

    def train(self, tokenized_sentences):
        for sentence in tokenized_sentences:
            for i in range(2, len(sentence)):
                context = (sentence[i - 2], sentence[i - 1])
                nxt = sentence[i]
                self.transition_counts[context][nxt] += 1
        self._calculate_probabilities()

    def _calculate_probabilities(self):
        for context, next_counts in self.transition_counts.items():
            total = sum(next_counts.values())
            self.probabilities[context] = {
                nxt: count / total
                for nxt, count in next_counts.items()
            }

    def get_distribution(self, context):
        return self.probabilities.get(tuple(context), {})

    def predict_next(self, context):
        distribution = self.get_distribution(context)
        if not distribution:
            return None
        return max(distribution, key=distribution.get)

    def sample_next(self, context):
        distribution = self.get_distribution(context)
        if not distribution:
            return None
        words = list(distribution)
        weights = list(distribution.values())
        return random.choices(words, weights=weights, k=1)[0]

    def _first_word(self, greedy=True):
        # The first word is conditioned on <START>.
        first_order_start = self.probabilities.get((START,), {})
        # We do not store this in the second-order CPT; infer it from
        # the training structure using the special START/the context.
        return None

    def generate_greedy(self, first_order_model, max_length=30):
        # First token: P(X1 | <START>)
        current = first_order_model.predict_next(START)
        if current is None or current == END:
            return ""

        output = [current]

        # Second token: P(X2 | <START>, X1)
        if len(output) >= max_length:
            return " ".join(output)

        previous = START
        for _ in range(max_length - 1):
            context = (previous, current)
            nxt = self.predict_next(context)

            if nxt is None or nxt == END:
                break

            output.append(nxt)
            previous, current = current, nxt

        return " ".join(output)

    def generate_sample(self, first_order_model, max_length=30):
        current = first_order_model.sample_next(START)
        if current is None or current == END:
            return ""

        output = [current]
        previous = START

        for _ in range(max_length - 1):
            context = (previous, current)
            nxt = self.sample_next(context)

            if nxt is None or nxt == END:
                break

            output.append(nxt)
            previous, current = current, nxt

        return " ".join(output)

    def check_normalization(self, tolerance=1e-9):
        results = {}
        for context, distribution in self.probabilities.items():
            total = sum(distribution.values())
            results[context] = (total, abs(total - 1.0) <= tolerance)
        return results


def print_probability_table(model):
    for context in sorted(model.probabilities, key=str):
        print(f"\n{context}")
        for nxt, p in sorted(model.probabilities[context].items()):
            print(f"  P({nxt}) = {p:.4f}")


def main():
    random.seed(42)

    data = tokenize_sentences(SENTENCES)

    first = FirstOrderLanguageModel()
    first.train(data)

    second = SecondOrderLanguageModel()
    second.train(data)

    print("=" * 70)
    print("FIRST-ORDER CPT")
    print("=" * 70)
    print_probability_table(first)

    print("\n" + "=" * 70)
    print("FIRST-ORDER NORMALIZATION")
    print("=" * 70)
    for context, (total, ok) in first.check_normalization().items():
        print(f"{context:10s} -> {total:.10f} -> {'PASS' if ok else 'FAIL'}")

    print("\n" + "=" * 70)
    print("NEXT-WORD PREDICTIONS")
    print("=" * 70)
    for context in [START, "the", "cat", "dog", "sat", "ran"]:
        print(f"{context:10s} -> {first.predict_next(context)}")
        print(f"             {first.get_distribution(context)}")

    print("\n" + "=" * 70)
    print("20 FIRST-ORDER SAMPLED SENTENCES")
    print("=" * 70)
    for i in range(20):
        print(f"{i+1:2d}. {first.generate_sample()}")

    print("\n" + "=" * 70)
    print("5 FIRST-ORDER GREEDY SENTENCES")
    print("=" * 70)
    for i in range(5):
        print(f"{i+1}. {first.generate_greedy()}")

    print("\n" + "=" * 70)
    print("5 FIRST-ORDER SAMPLED SENTENCES")
    print("=" * 70)
    for i in range(5):
        print(f"{i+1}. {first.generate_sample()}")

    print("\n" + "=" * 70)
    print("SECOND-ORDER CPT")
    print("=" * 70)
    print_probability_table(second)

    print("\n" + "=" * 70)
    print("SECOND-ORDER NORMALIZATION")
    print("=" * 70)
    for context, (total, ok) in second.check_normalization().items():
        print(f"{str(context):25s} -> {total:.10f} -> {'PASS' if ok else 'FAIL'}")

    print("\n" + "=" * 70)
    print("5 SECOND-ORDER GREEDY SENTENCES")
    print("=" * 70)
    for i in range(5):
        print(f"{i+1}. {second.generate_greedy(first)}")

    print("\n" + "=" * 70)
    print("5 SECOND-ORDER SAMPLED SENTENCES")
    print("=" * 70)
    for i in range(5):
        print(f"{i+1}. {second.generate_sample(first)}")

    vocabulary = set(t for sentence in data for t in sentence)

    first_parameters = sum(len(d) for d in first.probabilities.values())
    second_parameters = sum(len(d) for d in second.probabilities.values())

    first_zero_contexts = len(vocabulary - set(first.probabilities))
    second_zero_contexts = (
        len(vocabulary) ** 2 - len(second.probabilities)
    )

    print("\n" + "=" * 70)
    print("MODEL COMPARISON")
    print("=" * 70)
    print(f"Vocabulary size: {len(vocabulary)}")
    print(f"First-order observed probability entries: {first_parameters}")
    print(f"Second-order observed probability entries: {second_parameters}")
    print(f"First-order zero-probability contexts: {first_zero_contexts}")
    print(f"Second-order zero-probability contexts: {second_zero_contexts}")


if __name__ == "__main__":
    main()
