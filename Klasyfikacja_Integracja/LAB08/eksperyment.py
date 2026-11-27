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


def zadanie4():
    #porownanie sentymentu z koncowkami i bez koncowek (strip_cues=True)
    print("\nzadanie 4 - wplyw powtarzalnych koncowek (strip_cues=True)")
    lr_full = next(r for r in reports["sentiment"] if r["model"] == "Logistic Regression")
    _, stripped_reports = train("sentiment", strip_cues=True)
    lr_stripped = next(r for r in stripped_reports if r["model"] == "Logistic Regression")

    hits_full = round(lr_full["accuracy"] * lr_full["test_size"])
    hits_stripped = round(lr_stripped["accuracy"] * lr_stripped["test_size"])
    print(f"z koncowkami: accuracy={lr_full['accuracy']} ({hits_full}/{lr_full['test_size']}), macro_f1={lr_full['macro_f1']}")
    print(f"bez koncowek: accuracy={lr_stripped['accuracy']} ({hits_stripped}/{lr_stripped['test_size']}), macro_f1={lr_stripped['macro_f1']}")

    #wypisanie unikalnych koncowek po pierwszej kropce w reviews.csv
    raw_texts, raw_labels = load("sentiment", strip_cues=False)
    cues = {}
    for t, l in zip(raw_texts, raw_labels):
        tail = t.split(".", 1)[1].strip() if "." in t else ""
        cues.setdefault(l, set()).add(tail)
    for l in sorted(cues):
        print(f"koncowki {l} ({len(cues[l])}): {sorted(cues[l])[:3]}")

    #dodatkowe porownanie CountVectorizer vs TfidfVectorizer na tym samym podziale
    for strip in (False, True):
        texts, labels = load("sentiment", strip_cues=strip)
        x_tr, x_te, y_tr, y_te = train_test_split(texts, labels, test_size=0.25, random_state=42, stratify=labels)
        print(f"[CountVectorizer vs TF-IDF | strip_cues={strip}]")
        for vec_name, vec in [("TF-IDF", TfidfVectorizer(ngram_range=(1, 2))), ("Count", CountVectorizer(ngram_range=(1, 2)))]:
            for cls_name, est in [("NB", MultinomialNB()), ("LR", LogisticRegression(max_iter=1000)), ("SVM", LinearSVC())]:
                pipe = make_pipeline(vec, est)
                pipe.fit(x_tr, y_tr)
                pred = pipe.predict(x_te)
                acc = round(float(accuracy_score(y_te, pred)), 3)
                mf1 = round(float(f1_score(y_te, pred, average="macro")), 3)
                print(f"{vec_name} + {cls_name}: acc={acc}, macro_f1={mf1}")


def http_json(url, payload=None):
    #wyslanie prawdziwego zadania HTTP GET lub POST i zwrot statusu oraz body json
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json; charset=utf-8"} if payload is not None else {}
    req = urllib.request.Request(url, data=data, headers=headers, method="POST" if payload is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read().decode("utf-8"))


def zadanie5_api():
    #uruchomienie serwera app.py na porcie 5008 i wykonanie prawdziwych zapytan HTTP
    print("\nzadanie 5 - testy api na porcie 5008")
    base_url = "http://127.0.0.1:5008"
    app_path = Path(__file__).resolve().parent / "app.py"
    proc = subprocess.Popen(
        [sys.executable, str(app_path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        #czekanie na gotowosc serwera
        for _ in range(30):
            try:
                status, metrics = http_json(f"{base_url}/api/metrics")
                if status == 200:
                    break
            except Exception:
                time.sleep(0.25)
        else:
            raise RuntimeError("serwer app.py nie odpowiedzial na porcie 5008")

        #sprawdzenie /api/metrics i zgodnosci sumy macierzy z test_size
        for task in ("sentiment", "spam"):
            lr = next(r for r in metrics[task] if r["model"] == "Logistic Regression")
            matrix_sum = sum(sum(row) for row in lr["confusion"])
            print(f"GET /api/metrics [{task}]: status={status}, test_size={lr['test_size']}, matrix_sum={matrix_sum}")

        #test podstawowy i bledne zadania 400, 404, 413
        checks = [
            ("POST /api/classify/spam (poprawny)", f"{base_url}/api/classify/spam", {"text": "Kliknij link i podaj hasło"}),
            ("POST /api/classify/spam (pusty 400)", f"{base_url}/api/classify/spam", {"text": ""}),
            ("POST /api/classify/inne (nieznane 404)", f"{base_url}/api/classify/inne", {"text": "test"}),
            ("POST /api/classify/spam (za dlugi 413)", f"{base_url}/api/classify/spam", {"text": "a" * 4001}),
        ]
        for label, url, body in checks:
            st, res = http_json(url, body)
            print(f"{label} -> status={st}, body={res}")

        #seria zapytan podobnych oraz rozniacych sie slowem, koncowka, negacja lub kontekstem
        probes = [
            ("sentiment", "z koncowka", "Produkt działa szybko i stabilnie. Polecam ten zakup."),
            ("sentiment", "bez koncowki", "Produkt działa szybko i stabilnie"),
            ("sentiment", "pozytyw bez negacji", "Obsługa była szybka i pomocna"),
            ("sentiment", "ta sama fraza z negacja", "Obsługa nie była szybka ani pomocna"),
            ("sentiment", "poza csv pozytyw", "Telefon świetnie trzyma na baterii podczas wyjazdu"),
            ("sentiment", "poza csv negatyw", "Telefon strasznie krótko trzyma na baterii podczas wyjazdu"),
            ("sentiment", "poza csv neutral", "Telefon ma ekran OLED i waży 180 gramów"),
            ("spam", "link + nagroda/karta", "Kliknij link aby odebrać darmową nagrodę i podaj dane karty"),
            ("spam", "link sluzbowy (ham)", "Przesyłam link do notatek ze spotkania zespołu"),
            ("spam", "oplata/faktura sluzbowa", "Faktura za zamówienie i opłata za wysyłkę w załączniku"),
            ("spam", "paczka + doplata + link", "Twoja paczka czeka na pilną dopłatę kliknij link"),
        ]
        print("seria zapytan przez API:")
        for task, desc, txt in probes:
            st, res = http_json(f"{base_url}/api/classify/{task}", {"text": txt})
            print(f"[{task} | {desc}] status={st} -> label={res.get('label')}, prob={res.get('probability_estimate')} | '{txt}'")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    zadanie1()
    zadanie2()
    zadanie3()
    zadanie4()
    zadanie5_api()
