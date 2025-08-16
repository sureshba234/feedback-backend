
import csv, re, collections, json, argparse, os

def train(data_path: str, out_path: str):
    pos = collections.Counter()
    neg = collections.Counter()
    neu = collections.Counter()

    with open(data_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            text = row["text"].lower()
            words = re.findall(r"[a-z']+", text)
            label = row["label"].strip().lower()
            if label == "positive":
                pos.update(words)
            elif label == "negative":
                neg.update(words)
            else:
                neu.update(words)

    vocab = set(pos) | set(neg) | set(neu)
    weights = {}
    for w in vocab:
        p = pos[w] + 1
        n = neg[w] + 1
        u = neu[w] + 1
        score = (p - n) / (p + n + u)
        weights[w] = score

    model = {
        "type": "lexicon-v1",
        "weights": weights,
        "bias": 0.0,
        "threshold_pos": 0.05,
        "threshold_neg": -0.05
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(model, f)
    print(f"Saved model to {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=os.path.join(os.path.dirname(__file__), "..", "..", "sample_data", "feedback_labeled.csv"))
    parser.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "model.json"))
    args = parser.parse_args()
    train(args.data, args.out)
