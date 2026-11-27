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


if __name__ == "__main__":
    zadanie1()
