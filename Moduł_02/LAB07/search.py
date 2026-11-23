"""Trzy sposoby przeszukiwania tego samego archiwum 40 artykułów."""
from functools import lru_cache
import json
import os
from urllib.error import URLError
from urllib.request import Request, urlopen

import numpy as np

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lab6.search_engine import documents, search as bm25_search

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
ELASTIC_URL = os.environ.get("ELASTIC_URL", "http://127.0.0.1:9207").rstrip("/")
INDEX = "isi_articles_v1"


@lru_cache(maxsize=1)
def semantic_index():
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(MODEL_NAME, device="cpu")
    corpus = [doc["title"] + ". " + doc["text"] for doc in documents]
    vectors = model.encode_document(corpus, normalize_embeddings=True)
    return model, vectors


def semantic_search(query, top_k=5):
    model, vectors = semantic_index()
    vector = model.encode_query(query, normalize_embeddings=True)
    scores = np.asarray(vectors) @ np.asarray(vector)
    order = np.argsort(-scores, kind="stable")[:top_k]
    return [{"id": documents[i]["id"], "title": documents[i]["title"],
             "snippet": documents[i]["text"], "category": documents[i]["source"],
             "score": round(float(scores[i]), 4)} for i in order]


def elastic_request(method, path, payload=None, content_type="application/json"):
    data = payload if isinstance(payload, bytes) else json.dumps(payload).encode() if payload is not None else None
    req = Request(ELASTIC_URL + path, data=data, method=method,
                  headers={"Content-Type": content_type})
    with urlopen(req, timeout=5) as response:
        body = response.read()
    return json.loads(body) if body else {}


def elastic_ready():
    try:
        elastic_request("GET", "/")
        return True
    except (URLError, TimeoutError, OSError):
        return False


@lru_cache(maxsize=1)
def elastic_index():
    if not elastic_ready():
        raise ConnectionError("Elasticsearch nie odpowiada na " + ELASTIC_URL)
    try:
        elastic_request("GET", "/" + INDEX)
    except Exception as error:
        if getattr(error, "code", None) != 404:
            raise
        elastic_request("PUT", "/" + INDEX, {"mappings": {"properties": {
            "title": {"type": "text"}, "text": {"type": "text"},
            "source": {"type": "keyword"}}}})
    # ponytail: stały korpus 40 rekordów; po jego zmianie usuń indeks i restartuj proces.
    lines = []
    for doc in documents:
        lines.append(json.dumps({"index": {"_index": INDEX, "_id": doc["id"]}}, ensure_ascii=False))
        lines.append(json.dumps({"title": doc["title"], "text": doc["text"],
                                 "source": doc["source"]}, ensure_ascii=False))
    result = elastic_request("POST", "/_bulk?refresh=true", ("\n".join(lines) + "\n").encode(),
                             "application/x-ndjson")
    if result.get("errors"):
        raise RuntimeError("Elasticsearch zwrócił błąd indeksowania")


def elastic_search(query, top_k=5, fuzzy=False):
    elastic_index()
    match = {"query": query, "fields": ["title^2", "text"]}
    if fuzzy:
        match["fuzziness"] = "AUTO"
    response = elastic_request("POST", "/" + INDEX + "/_search", {
        "size": top_k,
        "query": {"multi_match": match}})
    return [{"id": int(hit["_id"]), "title": hit["_source"]["title"],
             "snippet": hit["_source"]["text"], "category": hit["_source"]["source"],
             "score": round(float(hit["_score"]), 4)} for hit in response["hits"]["hits"]]


def compare(query, top_k=5, fuzzy=False):
    result = {"query": query, "bm25": bm25_search(query, top_k),
              "semantic": None, "elastic": None}
    try:
        result["semantic"] = semantic_search(query, top_k)
    except (ImportError, OSError):
        result["semantic_error"] = (
            "Nie udało się załadować MiniLM. Zainstaluj zależności z requirements.txt "
            "i sprawdź, czy model jest zapisany lokalnie lub dostępny do pobrania."
        )
    if elastic_ready():
        result["elastic"] = elastic_search(query, top_k, fuzzy)
    return result


if __name__ == "__main__":
    print("BM25:", [item["title"] for item in bm25_search("komputer przenośny", 3)])
    print("Semantyczne:", [item["title"] for item in semantic_search("komputer przenośny", 3)])
    print("Elasticsearch:", "gotowy" if elastic_ready() else "wyłączony")
