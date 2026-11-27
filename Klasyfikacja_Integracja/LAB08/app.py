from pathlib import Path
import sys

lab_dir = str(Path(__file__).resolve().parent)
if lab_dir not in sys.path:
    sys.path.insert(0, lab_dir)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flask import Flask, jsonify, request, send_from_directory
from course import materials, page
if __package__:
    from .classifier import FILES, classify, reports
else:
    from classifier import FILES, classify, reports

app = Flask(__name__, static_folder="../assets", static_url_path="/assets")


@app.get("/")
def home():
    return send_from_directory(app.root_path, "index.html")


@app.get("/<name>")
def source(name):
    return page(8, name)


@app.get("/api/metrics")
def api_metrics():
    return jsonify(reports)


@app.post("/api/classify/<task>")
def api_classify(task):
    if task not in FILES:
        return jsonify({"error": "nieznane zadanie", "tasks": sorted(FILES)}), 404
    body = request.get_json(silent=True)
    text = body.get("text", "") if isinstance(body, dict) else ""
    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "podaj niepusty tekst w polu text"}), 400
    if len(text) > 4000:
        return jsonify({"error": "tekst jest za długi (maks. 4000 znaków)"}), 413
    return jsonify(classify(task, text))


app.register_blueprint(materials)


if __name__ == "__main__":
    app.run(debug=True, port=5008)
