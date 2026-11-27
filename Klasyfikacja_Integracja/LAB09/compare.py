"""Ta sama próbka opinii: Naive Bayes, mała sieć PyTorch, zamrożony Transformer."""
from functools import lru_cache
from pathlib import Path
import re
import sys
from time import perf_counter
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from lab8.classifier import load
from lab7.search import semantic_index

LABELS = ["negative", "neutral", "positive"]
EMBEDDING_DIM = 64
torch.set_num_threads(2)
TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def batches(texts, vocabulary):
    ids, offsets = [], []
    for text in texts:
        offsets.append(len(ids))
        ids.extend(vocabulary.get(token, 0) for token in TOKEN_RE.findall(text.lower()))
        if len(ids) == offsets[-1]:
            ids.append(0)
    return torch.tensor(ids, dtype=torch.long), torch.tensor(offsets, dtype=torch.long)


class ReviewNet(torch.nn.Module):
    def __init__(self, vocabulary_size):
        super().__init__()
        self.embedding = torch.nn.EmbeddingBag(vocabulary_size, EMBEDDING_DIM, mode="mean", padding_idx=0)
        self.head = torch.nn.Sequential(torch.nn.Linear(EMBEDDING_DIM, 64), torch.nn.ReLU(),
                                        torch.nn.Linear(64, len(LABELS)))

    def forward(self, ids, offsets):
        return self.head(self.embedding(ids, offsets))


def report(name, truth, predicted, inference_ms, texts):
    return {"model": name, "accuracy": round(float(accuracy_score(truth, predicted)), 3),
            "macro_f1": round(float(f1_score(truth, predicted, average="macro")), 3),
            "confusion": confusion_matrix(truth, predicted, labels=LABELS).tolist(),
            "test_size": len(truth), "inference_ms": round(inference_ms, 1),
            "errors": [{"text": text, "true_label": actual, "predicted_label": str(guess)}
                       for text, actual, guess in zip(texts, truth, predicted) if actual != guess]}


@lru_cache(maxsize=1)
def experiment():
    texts, labels = load("sentiment", strip_cues=True)
    x_train, x_test, y_train, y_test = train_test_split(
        texts, labels, test_size=.25, random_state=42, stratify=labels)
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    a = vectorizer.fit_transform(x_train)
    b = vectorizer.transform(x_test)

    bayes = MultinomialNB().fit(a, y_train)
    started = perf_counter()
    bayes_pred = bayes.predict(b)
    bayes_report = report("Naive Bayes", y_test, bayes_pred, (perf_counter() - started) * 1000, x_test)

    torch.manual_seed(42)
    vocabulary = {token: i + 1 for i, token in enumerate(sorted({
        token for text in x_train for token in TOKEN_RE.findall(text.lower())}))}
    net = ReviewNet(len(vocabulary) + 1)
    optimizer = torch.optim.Adam(net.parameters(), lr=.01)
    loss_fn = torch.nn.CrossEntropyLoss()
    train_batch = batches(x_train, vocabulary)
    test_batch = batches(x_test, vocabulary)
    targets = torch.tensor([LABELS.index(label) for label in y_train])
    for _ in range(60):
        optimizer.zero_grad()
        loss = loss_fn(net(*train_batch), targets)
        loss.backward()
        optimizer.step()
    net.eval()
    started = perf_counter()
    with torch.no_grad():
        net_pred = [LABELS[i] for i in net(*test_batch).argmax(1).tolist()]
    net_report = report("EmbeddingBag PyTorch", y_test, net_pred,
                        (perf_counter() - started) * 1000, x_test)

    encoder, _ = semantic_index()
    train_vectors = encoder.encode_document(x_train, normalize_embeddings=True)
    head = LogisticRegression(max_iter=1000).fit(train_vectors, y_train)
    started = perf_counter()
    test_vectors = encoder.encode_document(x_test, normalize_embeddings=True)
    transformer_pred = head.predict(test_vectors)
    transformer_report = report("MiniLM + LR", y_test, transformer_pred,
                                (perf_counter() - started) * 1000, x_test)
    return {"reports": [bayes_report, net_report, transformer_report],
            "models": (vectorizer, bayes, net, vocabulary, encoder, head)}


def predict(text):
    vectorizer, bayes, net, vocabulary, encoder, head = experiment()["models"]
    sparse = vectorizer.transform([text])
    with torch.no_grad():
        net_probabilities = net(*batches([text], vocabulary)).softmax(1)[0].tolist()
    vector = encoder.encode_document([text], normalize_embeddings=True)
    def decision(classes, probabilities):
        best = int(np.argmax(probabilities))
        return {"label": str(classes[best]), "score": round(float(probabilities[best]), 3)}

    return {"Naive Bayes": decision(bayes.classes_, bayes.predict_proba(sparse)[0]),
            "EmbeddingBag PyTorch": decision(LABELS, net_probabilities),
            "MiniLM + LR": decision(head.classes_, head.predict_proba(vector)[0])}


if __name__ == "__main__":
    for row in experiment()["reports"]:
        print(row)
    print(predict("Bateria szybko się wyczerpuje"))
