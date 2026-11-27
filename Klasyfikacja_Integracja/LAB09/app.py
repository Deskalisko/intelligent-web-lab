from pathlib import Path
import sys
lab_dir = str(Path(__file__).resolve().parent)
if lab_dir not in sys.path:
    sys.path.insert(0, lab_dir)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flask import Flask, jsonify, request, send_from_directory
from course import materials, page
if __package__:
    from .compare import experiment, predict
else:
    from compare import experiment, predict

app = Flask(__name__, static_folder="../assets", static_url_path="/assets")


@app.get("/")
def home():
    return send_from_directory(app.root_path, "index.html")


@app.get("/<name>")
def illustration(name):
    return page(9, name)


@app.get("/api/metrics")
def metrics():
    #raport porownawczy trzech modeli na wspolnym zbiorze testowym
    return jsonify({"labels": ["negative", "neutral", "positive"],
                    "reports": experiment()["reports"],
                    "note": "54 sztuczne opinie; powtarzalne końcówki usunięte; test 14 tekstów"})


@app.post("/api/predict")
@app.post("/api/classify/deep")
def api_predict():
    #walidacja pustego tekstu (400) i limitu 4000 znakow (413)
    body = request.get_json(silent=True)
    text = body.get("text", "") if isinstance(body, dict) else ""
    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "podaj niepusty tekst w polu text"}), 400
    if len(text) > 4000:
        return jsonify({"error": "tekst jest za długi (maks. 4000 znaków)"}), 413
    return jsonify({"text": text, "predictions": predict(text)})


app.register_blueprint(materials)


if __name__ == "__main__":
    app.run(debug=True, port=5009)
