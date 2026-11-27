from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flask import Flask, jsonify, request, send_from_directory
from course import materials, page
if __package__:
    from .search_engine import documents, index, search, suggest
else:
    from search_engine import documents, index, search, suggest

app = Flask(__name__, static_folder="../assets", static_url_path="/assets")


@app.get("/")
def home():
    return send_from_directory(app.root_path, "index.html")

@app.get("/<name>")
def source(name):
    return page(6, name)

@app.get("/api/search")
def api_search():
    query = request.args.get("q", "").strip()
    top_k_raw = request.args.get("top_k", "10")
    category = request.args.get("category", "").strip()
    
    #zbiór unikalnych kategorii występujących w bazie dokumentów
    categories = {doc["source"] for doc in documents}
    
    #nie może być puste i nie może przekraczać 200 znaków
    if not query or len(query) > 200:
        return jsonify({"error": "q musi mieć od 1 do 200 znaków"}), 400
        
    #walidacja liczby wyników top_k
    if len(top_k_raw) > 2 or not top_k_raw.isdecimal() or not 1 <= int(top_k_raw) <= 20:
        return jsonify({"error": "top_k musi być od 1 do 20"}), 400
    top_k = int(top_k_raw)
    
    #walidacja kategorii
    if category and category not in categories:
        category = next((name for name in categories if name.casefold() == category.casefold()), None)
        if category is None:
            return jsonify({"error": "nieznana kategoria", "categories": sorted(categories)}), 400
            
    #wyszukanie dopasowanych artykułów przez BM25
    results = search(query, top_k, category or None)
    
    #zwrócenie wyników oraz ewentualnych sugestii poprawy literówek
    return jsonify({
        "query": query,
        "count": len(results),
        "results": results,
        "suggestions": suggest(query)
    })


@app.get("/api/index/<term>")
def api_index(term):
    #podgląd wystąpień danego słowa w odwróconym indeksie
    posting = index.get(term.casefold())
    return jsonify({
        "term": term,
        "postings": posting or {},
        "document_frequency": len(posting or {})
    })


app.register_blueprint(materials)

#PRZYKŁADOWE TESTY API
#
#Prawidłowe wyszukiwanie:
#curl "http://127.0.0.1:5006/api/search?q=procesor&top_k=3"
#Invoke-RestMethod -Uri "http://127.0.0.1:5006/api/search?q=procesor&top_k=3"
#
#Wyszukiwanie z filtrem kategorii:
#curl "http://127.0.0.1:5006/api/search?q=trening&category=Sport"
#
#Wyszukiwanie z literówką (zwraca puste results i pole suggestions):
#
#curl "http://127.0.0.1:5006/api/search?q=procezor"
#
#Sprawdzenie wpisu w indeksie odwróconym:
#curl "http://127.0.0.1:5006/api/index/technologia"
#
#Błąd walidacji - puste zapytanie(400):
# curl "http://127.0.0.1:5006/api/search?q="

if __name__ == "__main__":
    app.run(debug=True, port=5006)
