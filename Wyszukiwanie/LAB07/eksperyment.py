from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from search import bm25_search, semantic_search, elastic_search, elastic_ready, documents, semantic_index


if __name__ == "__main__":
    #zapytanie doslowne vs parafraza (cel: art 1)
    q_doslowne = "nowy procesor laptopów"
    q_parafraza = "komputer przenośny do pracy"

    r_bm25_dosl = bm25_search(q_doslowne, top_k=1)
    r_sem_dosl = semantic_search(q_doslowne, top_k=1)
    print("doslowne bm25:", [(r["id"], r["score"]) for r in r_bm25_dosl])
    print("doslowne minilm:", [(r["id"], r["score"]) for r in r_sem_dosl])

    r_bm25_par = bm25_search(q_parafraza, top_k=1)
    r_sem_par = semantic_search(q_parafraza, top_k=1)
    print("parafraza bm25:", [(r["id"], r["score"]) for r in r_bm25_par])
    print("parafraza minilm:", [(r["id"], r["score"]) for r in r_sem_par])

    #literowka procezor
    print("literowka bm25:", bm25_search("procezor", top_k=1))
    print("literowka minilm:", [(r["id"], r["score"]) for r in semantic_search("procezor", top_k=1)])
    if elastic_ready():
        print("literowka elastic bez fuzzy:", elastic_search("procezor", top_k=1, fuzzy=False))
        print("literowka elastic z fuzzy:", [(r["id"], r["score"]) for r in elastic_search("procezor", top_k=1, fuzzy=True)])
    else:
        print("elastic: brak pomiaru (kontener wylaczony)")

    #recall@3 na 5 zapytaniach testowych
    pytania = [
        {"q": "komputer przenośny do pracy", "target": 1},
        {"q": "nowoczesny aparat do fotografii w ciemności", "target": 2},
        {"q": "bieg maratoński ulicami", "target": 10},
        {"q": "spektakl muzyczny orkiestry w teatrze", "target": 27},
        {"q": "ocieplenie wód w zbiornikach wodnych", "target": 40}
    ]

    bm25_hits = 0
    sem_hits = 0
    print("\ntesty recall@3:")
    for p in pytania:
        res_b = [r["id"] for r in bm25_search(p["q"], top_k=3)]
        res_s = [r["id"] for r in semantic_search(p["q"], top_k=3)]
        hit_b = 1 if p["target"] in res_b else 0
        hit_s = 1 if p["target"] in res_s else 0
        bm25_hits += hit_b
        sem_hits += hit_s
        print(f"'{p['q']}' -> cel {p['target']} | bm25: {hit_b} {res_b} | minilm: {hit_s} {res_s}")

    print(f"\nrecall@3 bm25: {bm25_hits / len(pytania):.2f}")
    print(f"recall@3 minilm: {sem_hits / len(pytania):.2f}")

    #usuniecie szablonu redakcyjnego i wplyw na minilm
    #w bm25 wynik wzrastal z 4.407 do 4.826 przez mniejsza kare za dlugosc
    szablon = "Technologia i urządzenia będą testowane przez użytkowników."
    art1 = next(d for d in documents if d["id"] == 1)
    art1_bez = art1["text"].replace(szablon, "").strip()
    
    model, _ = semantic_index()
    v_orig = model.encode(art1["title"] + ". " + art1["text"], normalize_embeddings=True)
    v_bez = model.encode(art1["title"] + ". " + art1_bez, normalize_embeddings=True)
    v_q = model.encode(q_doslowne, normalize_embeddings=True)
    
    cos_orig = float(np.dot(v_orig, v_q))
    cos_bez = float(np.dot(v_bez, v_q))
    print(f"\nart 1 przed i po usunieciu szablonu (minilm): {cos_orig:.4f} -> {cos_bez:.4f}")

    #proba wlasna z parafraza
    wlasna = "sprzęt do gier i szybka grafika"
    print(f"\nwlasna proba '{wlasna}' (cel art 8):")
    print("bm25:", [(r["id"], r["score"]) for r in bm25_search(wlasna, top_k=3)])
    print("minilm:", [(r["id"], r["score"]) for r in semantic_search(wlasna, top_k=3)])
