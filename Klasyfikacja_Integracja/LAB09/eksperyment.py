from collections import Counter
from pathlib import Path
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request

from sklearn.model_selection import train_test_split

#dodanie folderu LAB09 oraz katalogu glownego do sys.path
lab_dir = str(Path(__file__).resolve().parent)
root_dir = str(Path(__file__).resolve().parents[2])
for p in (lab_dir, root_dir):
    if p not in sys.path:
        sys.path.insert(0, p)

import compare
from Klasyfikacja_Integracja.LAB08.classifier import load


def zadanie1():
    #wspolny podzial 40 train / 14 test bez powtarzalnych koncowek
    print("zadanie 1 - wspolny test bez koncowek (strip_cues=True)")
    texts, labels = load("sentiment", strip_cues=True)
    x_train, x_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.25, random_state=42, stratify=labels
    )
    print(f"all={len(texts)} -> train={len(x_train)} {dict(sorted(Counter(y_train).items()))}, test={len(x_test)} {dict(sorted(Counter(y_test).items()))}")
    reports = compare.experiment()["reports"]
    for r in reports:
        print(f"{r['model']}: test_size={r['test_size']}")


if __name__ == "__main__":
    zadanie1()
