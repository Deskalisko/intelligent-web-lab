from collections import Counter
from pathlib import Path
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request

from sklearn.model_selection import train_test_split

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


def zadanie2():
    #zestawienie accuracy, macro_f1, macierzy pomylek i czasu predykcji dla 3 modeli
    print("\nzadanie 2 - wyniki 3 modeli i czas predykcji")
    reports = compare.experiment()["reports"]
    for r in reports:
        print(
            f"{r['model']}: accuracy={r['accuracy']}, macro_f1={r['macro_f1']}, "
            f"inference_ms={r['inference_ms']}, confusion={r['confusion']}"
        )
    by_acc = [r["model"] for r in sorted(reports, key=lambda x: x["accuracy"], reverse=True)]
    by_f1 = [r["model"] for r in sorted(reports, key=lambda x: x["macro_f1"], reverse=True)]
    print(f"kolejnosc accuracy: {by_acc}")
    print(f"kolejnosc macro_f1: {by_f1}")


def http_json(url, payload=None):
    #wyslanie zadania HTTP GET lub POST i zwrot statusu oraz body json
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json; charset=utf-8"} if payload is not None else {}
    req = urllib.request.Request(url, data=data, headers=headers, method="POST" if payload is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read().decode("utf-8"))


def start_server():
    #uruchomienie app.py na porcie 5009 i oczekiwanie na gotowosc /api/metrics
    base_url = "http://127.0.0.1:5009"
    app_path = Path(__file__).resolve().parent / "app.py"
    proc = subprocess.Popen(
        [sys.executable, str(app_path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(90):
        try:
            st, _ = http_json(f"{base_url}/api/metrics")
            if st == 200:
                return proc, base_url
        except Exception:
            time.sleep(0.5)
    proc.terminate()
    raise RuntimeError("serwer LAB09 app.py nie odpowiedzial na porcie 5009")


def zadanie3_api():
    #testy rozbieznosci trzech modeli przez zywe API na porcie 5009
    print("\nzadanie 3 - rozbieznosci modeli przez API (port 5009)")
    proc, base_url = start_server()
    try:
        st, _ = http_json(f"{base_url}/api/metrics")
        print(f"GET /api/metrics -> status={st}")
        probes = [
            ("przeczenie1_neg", "Bateria szybko się wyczerpuje"),
            ("przeczenie1_pos", "Bateria nie wyczerpuje się szybko"),
            ("przeczenie2_pos", "Aplikacja działa płynnie"),
            ("przeczenie2_neg", "Aplikacja nie działa płynnie"),
            ("kolejnosc_A", "Produkt dobry, serwis kiepski"),
            ("kolejnosc_B", "Produkt kiepski, serwis dobry"),
            ("mieszane", "Obsługa szybko pomogła, ale obudowa pękła po tygodniu"),
            ("parafraza_neg", "Cena jest wysoka jak na takie wykonanie"),
            ("parafraza_pos", "Ekran ma bardzo żywe kolory i dobrze wygląda"),
        ]
        for tag, text in probes:
            st, res = http_json(f"{base_url}/api/predict", {"text": text})
            preds = res["predictions"]
            summary = " | ".join(f"{m}: {v['label']} ({v['score']})" for m, v in preds.items())
            print(f"[{tag}] '{text}' -> {summary}")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    zadanie1()
    zadanie2()
    zadanie3_api()
