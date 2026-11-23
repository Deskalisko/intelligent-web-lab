"""Lab 6: odwrócony indeks i BM25 na archiwum artykułów z Lab 4."""
from collections import Counter, defaultdict
import csv
from difflib import get_close_matches
from math import log
from pathlib import Path
import re

DATA = Path(__file__).resolve().parents[1] / "lab4" / "articles.csv"
STOP = {"i", "w", "na", "do", "z", "o", "po", "dla", "oraz", "nad", "przed", "że", "się", "jest", "ma", "są"}
K1 = 1.2
B = 0.75


def tokenize(text):
    return [word for word in re.findall(r"[^\W_]+", text.lower(), flags=re.UNICODE)
            if len(word) > 1 and word not in STOP]


with DATA.open(encoding="utf-8", newline="") as file:
    documents = [{**row, "id": int(row["id"])} for row in csv.DictReader(file)]
by_id = {doc["id"]: doc for doc in documents}
index = defaultdict(dict)  # token -> {doc_id: frequency}
lengths = {}
for doc in documents:
    counts = Counter(tokenize(doc["title"] + " " + doc["text"]))
    lengths[doc["id"]] = sum(counts.values())
    for term, frequency in counts.items():
        index[term][doc["id"]] = frequency
AVGDL = sum(lengths.values()) / len(documents)


def bm25(term, doc_id):
    """Wariant IDF używany przez Lucene BM25Similarity."""
    posting = index.get(term, {})
    tf = posting.get(doc_id, 0)
    if not tf:
        return 0.0
    n = len(documents)
    df = len(posting)
    idf = log(1 + (n - df + 0.5) / (df + 0.5))
    norm = K1 * (1 - B + B * lengths[doc_id] / AVGDL)
    return idf * tf * (K1 + 1) / (tf + norm)


def search(query, top_k=10, category=None):
    if type(top_k) is not int or top_k < 1:
        raise ValueError("top_k musi być dodatnią liczbą całkowitą")
    terms = set(tokenize(query))
    candidates = set().union(*(index.get(term, {}) for term in terms)) if terms else set()
    results = []
    for doc_id in candidates:
        doc = by_id[doc_id]
        if category and doc["source"].casefold() != category.casefold():
            continue
        score = sum(bm25(term, doc_id) for term in terms)
        results.append({"id": doc_id, "title": doc["title"], "snippet": doc["text"],
                        "category": doc["source"], "score": score})
    results = sorted(results, key=lambda item: (-item["score"], item["id"]))[:top_k]
    for result in results:
        result["score"] = round(result["score"], 4)
    return results


def suggest(query):
    matches = {}
    for term in tokenize(query):
        if term not in index:
            close = get_close_matches(term, index.keys(), n=1, cutoff=0.72)
            if close:
                matches[term] = close[0]
    return matches


if __name__ == "__main__":
    print(f"{len(documents)} dokumentów, {len(index)} haseł, średnia długość {AVGDL:.1f} tokenów")
    print("technologia urządzenia:")
    for result in search("technologia urządzenia", top_k=5):
        print(f"  {result['score']:.3f}  {result['title']}")
    print("indeks['technologia']:", index.get("technologia", {}))
