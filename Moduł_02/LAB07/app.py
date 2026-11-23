from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flask import Flask, jsonify, request, send_from_directory
from course import materials, page
if __package__:
    from .search import compare, elastic_ready
else:
    from search import compare, elastic_ready

app = Flask(__name__, static_folder="../assets", static_url_path="/assets")


@app.get("/")
def home():
    return send_from_directory(app.root_path, "index.html")


@app.get("/<name>")
def illustration(name):
    return page(7, name)


@app.get("/api/status")
def status():
    return jsonify({"elastic": elastic_ready(), "semantic": "model ładowany przy pierwszym zapytaniu"})


@app.get("/api/compare")
def api_compare():
    query = request.args.get("q", "").strip()
    if not query or len(query) > 200:
        return jsonify({"error": "q musi mieć od 1 do 200 znaków"}), 400
    try:
        top_k = int(request.args.get("top_k", "5"))
    except ValueError:
        return jsonify({"error": "top_k musi być liczbą"}), 400
    if not 1 <= top_k <= 10:
        return jsonify({"error": "top_k musi być od 1 do 10"}), 400
    fuzzy = request.args.get("fuzzy", "0")
    if fuzzy not in ("0", "1"):
        return jsonify({"error": "fuzzy musi być 0 albo 1"}), 400
    try:
        return jsonify(compare(query, top_k, fuzzy == "1"))
    except ConnectionError as error:
        return jsonify({"error": str(error)}), 503


app.register_blueprint(materials)


if __name__ == "__main__":
    app.run(debug=True, port=5007)
