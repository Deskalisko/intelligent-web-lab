from functools import lru_cache
import json
import os
from pathlib import Path
import sys
from urllib.error import URLError
from urllib.request import Request, urlopen

import numpy as np

#importujemy baze i wyszukiwarke z lab6
parent_dir = str(Path(__file__).resolve().parents[1])
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from LAB06.search_engine import documents, search as bm25_search
except ImportError:
    from lab6.search_engine import documents, search as bm25_search

#model wielojezyczny do embeddingow (384 wymiary)
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

#adres lokalnego elastica z docker compose
ELASTIC_URL = os.environ.get("ELASTIC_URL", "http://127.0.0.1:9207").rstrip("/")
INDEX = "isi_articles_v1"


def _encode_docs(model, corpus):
    #pomocnicze kodowanie dokumentow z normalizacja wektorow
    if hasattr(model, "encode_document"):
        return model.encode_document(corpus, normalize_embeddings=True)
    return model.encode(corpus, normalize_embeddings=True)


def _encode_query(model, query):
    #pomocnicze kodowanie zapytania uzytkownika
    if hasattr(model, "encode_query"):
        return model.encode_query(query, normalize_embeddings=True)
    return model.encode(query, normalize_embeddings=True)


@lru_cache(maxsize=1)
def semantic_index():
    #lru_cache zeby model ladowac i wektory liczyc tylko raz
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(MODEL_NAME, device="cpu")
    corpus = [doc["title"] + ". " + doc["text"] for doc in documents]
    vectors = _encode_docs(model, corpus)
    return model, vectors


def semantic_search(query, top_k=5):
    #kodujemy zapytanie do wektora
    model, vectors = semantic_index()
    vector = _encode_query(model, query)
    
    #iloczyn skalarny znormalizowanych wektorow to dokladnie cosinus kata
    scores = np.asarray(vectors) @ np.asarray(vector)
    order = np.argsort(-scores, kind="stable")[:top_k]
    
    return [{
        "id": documents[i]["id"],
        "title": documents[i]["title"],
        "snippet": documents[i]["text"],
        "category": documents[i]["source"],
        "score": round(float(scores[i]), 4)
    } for i in order]


def elastic_request(method, path, payload=None, content_type="application/json"):
    #pomocnicza funkcja do strzalow http do elastica
    data = payload if isinstance(payload, bytes) else json.dumps(payload).encode() if payload is not None else None
    req = Request(
        ELASTIC_URL + path,
        data=data,
        method=method,
        headers={"Content-Type": content_type}
    )
    with urlopen(req, timeout=5) as response:
        body = response.read()
    return json.loads(body) if body else {}


def elastic_ready():
    #sprawdza czy kontener elastica wstaje i odpowiada
    try:
        elastic_request("GET", "/")
        return True
    except (URLError, TimeoutError, OSError):
        return False


@lru_cache(maxsize=1)
def elastic_index():
    #zaklada indeks w elasticsearch i wrzuca 40 artykulow przez bulk api
    if not elastic_ready():
        raise ConnectionError("Elasticsearch nie odpowiada na " + ELASTIC_URL)
    try:
        elastic_request("GET", "/" + INDEX)
    except Exception as error:
        if getattr(error, "code", None) != 404:
            raise
        #mapowanie: title i text jako pelny tekst, source jako keyword
        elastic_request("PUT", "/" + INDEX, {
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "text": {"type": "text"},
                    "source": {"type": "keyword"}
                }
            }
        })
        
    lines = []
    for doc in documents:
        lines.append(json.dumps({"index": {"_index": INDEX, "_id": doc["id"]}}, ensure_ascii=False))
        lines.append(json.dumps({
            "title": doc["title"],
            "text": doc["text"],
            "source": doc["source"]
        }, ensure_ascii=False))
        
    result = elastic_request(
        "POST",
        "/_bulk?refresh=true",
        ("\n".join(lines) + "\n").encode("utf-8"),
        "application/x-ndjson"
    )
    if result.get("errors"):
        raise RuntimeError("Elasticsearch zwrócił błąd indeksowania")


def elastic_search(query, top_k=5, fuzzy=False):
    #szukanie przez multi_match: tytul ma 2x wieksza wage (title^2)
    elastic_index()
    match = {
        "query": query,
        "fields": ["title^2", "text"]
    }
    if fuzzy:
        match["fuzziness"] = "AUTO"
        
    response = elastic_request("POST", "/" + INDEX + "/_search", {
        "size": top_k,
        "query": {"multi_match": match}
    })
    
    return [{
        "id": int(hit["_id"]),
        "title": hit["_source"]["title"],
        "snippet": hit["_source"]["text"],
        "category": hit["_source"]["source"],
        "score": round(float(hit["_score"]), 4)
    } for hit in response["hits"]["hits"]]


def compare(query, top_k=5, fuzzy=False):
    #zbiera wyniki z bm25, semantyki i elastica w jeden slownik
    result = {
        "query": query,
        "bm25": bm25_search(query, top_k),
        "semantic": None,
        "elastic": None
    }
    
    try:
        result["semantic"] = semantic_search(query, top_k)
    except Exception as e:
        result["semantic_error"] = str(e)
        
    if elastic_ready():
        try:
            result["elastic"] = elastic_search(query, top_k, fuzzy)
        except Exception as e:
            result["elastic_error"] = str(e)
            
    return result


if __name__ == "__main__":
    test_q = "komputer przenośny"
    print("zapytanie parafraza:", test_q)
    
    bm25_res = bm25_search(test_q, top_k=3)
    print("bm25 trafienia:", len(bm25_res))
    for r in bm25_res:
        print(f"  ID {r['id']} | score {r['score']} | {r['title']}")
        
    sem_res = semantic_search(test_q, top_k=3)
    print("semantyczne minilm:")
    for r in sem_res:
        print(f"  ID {r['id']} | score {r['score']} | {r['title']}")
        
    print("elastic gotowy:", elastic_ready())
