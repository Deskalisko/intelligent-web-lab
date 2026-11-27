from collections import Counter
from pathlib import Path
import csv
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.svm import LinearSVC

#dodanie folderu LAB08 do sys.path zeby import dzialal z dowolnego katalogu
lab_dir = str(Path(__file__).resolve().parent)
if lab_dir not in sys.path:
    sys.path.insert(0, lab_dir)

from classifier import FILES, classify, load, reports, train


def zadanie1():
    #podzial 75/25 ze stratyfikacja i fit slownika TF-IDF wylacznie na zbiorze treningowym
    print("zadanie 1 - przygotowanie danych i podzial train/test przed fit TF-IDF")
    for task in ("sentiment", "spam"):
        texts, labels = load(task)
        x_train, x_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.25, random_state=42, stratify=labels
        )
        vec = TfidfVectorizer(ngram_range=(1, 2)).fit(x_train)
        print(
            f"[{task}] all={len(texts)} -> train={len(x_train)}, test={len(x_test)} | "
            f"train_klasy={dict(sorted(Counter(y_train).items()))} | "
            f"test_klasy={dict(sorted(Counter(y_test).items()))} | "
            f"slownik_tfidf_train={len(vec.vocabulary_)}"
        )


def zadanie2():
    #porownanie accuracy, macro_f1 i macierzy pomylek dla 3 klasyfikatorow
    print("\nzadanie 2 - porownanie trzech modeli")
    for task in ("sentiment", "spam"):
        print(f"[{task}]")
        for row in reports[task]:
            print(
                f"{row['model']}: accuracy={row['accuracy']}, macro_f1={row['macro_f1']}, "
                f"test_size={row['test_size']}, confusion={row['confusion']}"
            )


def find_csv_line(task, text_fragment):
    #szukanie numeru linii w pliku csv dla konkretnego tekstu
    with FILES[task].open(encoding="utf-8", newline="") as f:
        for idx, row in enumerate(csv.DictReader(f), start=2):
            if text_fragment in row["text"]:
                return idx
    return None


def zadanie3():
    #odczytanie pomylek poza przekatna macierzy dla Logistic Regression
    print("\nzadanie 3 - pomylki poza przekatna macierzy (Logistic Regression)")
    for task in ("sentiment", "spam"):
        lr = next(r for r in reports[task] if r["model"] == "Logistic Regression")
        print(f"[{task}] labels={lr['labels']} confusion={lr['confusion']}")
        for err in lr["errors"]:
            line_no = find_csv_line(task, err["text"])
            print(
                f"linia_csv={line_no} | true={err['true_label']} -> pred={err['predicted_label']} | text={err['text']}"
            )


if __name__ == "__main__":
    zadanie1()
    zadanie2()
    zadanie3()
