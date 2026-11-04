from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flask import Flask, jsonify, request, send_from_directory
from course import materials, page
if __package__:
    from .compare import EPS, MIN_SAMPLES, articles, assign_near_core, compare, dbscan
else:
    from compare import EPS, MIN_SAMPLES, articles, assign_near_core, compare, dbscan

app = Flask(__name__, static_folder="../assets", static_url_path="/assets")


@app.get("/")
def home():
    return send_from_directory(app.root_path, "index.html")


@app.get("/<name>")
def source(name):
    return page(5, name)


@app.get("/api/compare")
def api_compare():
    return jsonify({"eps": EPS, "min_samples": MIN_SAMPLES, "results": compare()})


@app.get("/api/noise")
def api_noise():
    return jsonify([{"id": int(article["id"]), "title": article["title"]}
                    for article, label in zip(articles, dbscan.labels_) if label == -1])


@app.post("/api/cluster/assign")
def api_assign():
    body = request.get_json(silent=True)
    text = body.get("text", "") if isinstance(body, dict) else ""
    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "podaj niepusty tekst w polu text"}), 400
    if len(text) > 4000:
        return jsonify({"error": "tekst jest za długi (maks. 4000 znaków)"}), 413
    return jsonify(assign_near_core(text))


app.register_blueprint(materials)


if __name__ == "__main__":
    app.run(debug=True, port=5005)
