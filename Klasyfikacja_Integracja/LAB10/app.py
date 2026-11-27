"""Lab 10: jeden interfejs i API dla modeli oraz indeksu z wcześniejszych zajęć."""
from html import escape
from pathlib import Path
import sys
lab_dir = str(Path(__file__).resolve().parent)
root_dir = str(Path(__file__).resolve().parents[2])
if lab_dir not in sys.path:
    sys.path.insert(0, lab_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from flask import Flask, jsonify, request, send_from_directory
from course import materials, page
from Rekomendacje.LAB02.recommender import df as movies, recommend as by_content    
from Rekomendacje.LAB03.recommender import matrix as ratings, recommend as by_user
from Wyszukiwanie.LAB06.search_engine import documents, search
from Klasyfikacja_Integracja.LAB08.classifier import classify

app = Flask(__name__, static_folder="../assets", static_url_path="/assets")


@app.get("/")
def home():
    return send_from_directory(app.root_path, "index.html")


@app.get("/<name>")
def illustration(name):
    return page(10, name)


@app.get("/project")
@app.get("/plan")
def project_docs():
    name = "PLAN.md" if request.path == "/plan" else "README.md"
    content = escape((Path(app.root_path) / name).read_text(encoding="utf-8"))
    return (f'<!doctype html><html lang="pl"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{name} · Lab 10</title>'
            '<style>body{max-width:900px;margin:3rem auto;padding:0 1.5rem;background:#0e2027;'
            'color:#d7f6f3;font:17px/1.6 system-ui}a{color:#ff82ac}pre{white-space:pre-wrap;'
            'overflow-wrap:anywhere;font:inherit}</style><a href="/">← Lab 10</a>'
            f'<pre>{content}</pre></html>')


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "movies": len(movies), "users": len(ratings),
                    "articles": len(documents), "services": ["content", "collaborative", "search", "feedback"]})


@app.get("/api/catalog")
def catalog():
    return jsonify({"movies": sorted(movies["title"].tolist()), "users": sorted(ratings.index.tolist())})


def top_n():
    try:
        count = int(request.args.get("top_n", "5"))
    except ValueError:
        return None
    return count if 1 <= count <= 10 else None


@app.get("/api/recommend/content")
def content_recommend():
    title = request.args.get("title", "").strip()
    count = top_n()
    if not title or count is None:
        return jsonify({"error": "podaj title i top_n od 1 do 10"}), 400
    result = by_content(title, top_n=count)
    return jsonify({"query": title, "results": result}) if result is not None else (
        jsonify({"error": "nie znam takiego filmu"}), 404)


@app.get("/api/recommend/collaborative")
def collaborative_recommend():
    user = request.args.get("user", "").strip()
    count = top_n()
    if not user or count is None:
        return jsonify({"error": "podaj user i top_n od 1 do 10"}), 400
    result = by_user(user, top_n=count)
    return jsonify({"query": user, "results": result}) if result is not None else (
        jsonify({"error": "nie znam takiego użytkownika"}), 404)


@app.get("/api/search")
def api_search():
    query = request.args.get("q", "").strip()
    count = top_n()
    if not query or len(query) > 200 or count is None:
        return jsonify({"error": "podaj q (1-200 znaków) i top_n od 1 do 10"}), 400
    return jsonify({"query": query, "results": search(query, count)})


@app.post("/api/feedback")
def feedback():
    body = request.get_json(silent=True)
    text = body.get("text", "") if isinstance(body, dict) else ""
    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "podaj niepusty tekst w polu text"}), 400
    if len(text) > 4000:
        return jsonify({"error": "tekst jest za długi (maks. 4000 znaków)"}), 413
    return jsonify(classify("sentiment", text))


app.register_blueprint(materials)


if __name__ == "__main__":
    app.run(debug=True, port=5010)
