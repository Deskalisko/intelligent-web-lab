"""Lab 8: dwa zbiory, trzy klasyfikatory, jeden uczciwy podział train/test."""
import csv
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.svm import LinearSVC

ROOT = Path(__file__).resolve().parent
FILES = {"sentiment": ROOT / "reviews.csv", "spam": ROOT / "emails.csv"}


def load(task, strip_cues=False):
    with FILES[task].open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    texts = [row["text"].split(".", 1)[0] if strip_cues and task == "sentiment" else row["text"]
             for row in rows]
    return texts, [row["label"] for row in rows]


def train(task, strip_cues=False):
    texts, labels = load(task, strip_cues)
    x_train, x_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.25, random_state=42, stratify=labels
    )
    estimators = {
        "Naive Bayes": MultinomialNB(),
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "Linear SVM": LinearSVC(),
    }
    report = []
    fitted = {}
    classes = sorted(set(labels))
    for name, estimator in estimators.items():
        model = make_pipeline(TfidfVectorizer(ngram_range=(1, 2)), estimator)
        model.fit(x_train, y_train)
        predicted = model.predict(x_test)
        fitted[name] = model
        report.append({"model": name, "accuracy": round(float(accuracy_score(y_test, predicted)), 3),
                       "macro_f1": round(float(f1_score(y_test, predicted, average="macro")), 3),
                       "confusion": confusion_matrix(y_test, predicted, labels=classes).tolist(),
                       "labels": classes, "test_size": len(y_test),
                       "errors": [{"text": text, "true_label": truth, "predicted_label": str(guess)}
                                  for text, truth, guess in zip(x_test, y_test, predicted)
                                  if truth != guess]})
    return fitted, report


models = {}
reports = {}
for task in FILES:
    models[task], reports[task] = train(task)


def classify(task, text):
    model = models[task]["Logistic Regression"]
    probabilities = model.predict_proba([text])[0]
    winner = int(probabilities.argmax())
    return {"task": task, "label": str(model.classes_[winner]),
            "probability_estimate": round(float(probabilities[winner]), 3),
            "model": "Logistic Regression"}


if __name__ == "__main__":
    for task in FILES:
        print(task, reports[task])
    print(classify("sentiment", "Obsługa była szybka i uprzejma"))
    print(classify("spam", "Kliknij link i podaj hasło"))
    _, without_cues = train("sentiment", strip_cues=True)
    print("sentiment bez powtarzalnych końcówek:", without_cues)
