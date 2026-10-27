from flask import Flask, jsonify, request
from recommender import recommend

app = Flask(__name__)

@app.route("/api/recommend")
def api_recommend():
    title = request.args.get("title", "").strip()
    if not title:
        return jsonify({"error": "podaj parametr ?title=..."}), 400
    n = request.args.get("top_n", type=int) if "top_n" in request.args else 5
    if n is None or not 1 <= n <= 10:
        return jsonify({"error": "top_n musi byc z zakresu 1-10"}), 400
    recs = recommend(title, top_n=n)
    if recs is None:
        return jsonify({"error": "nie znam takiego filmu"}), 404
    return jsonify({"title": title, "count": len(recs), "recommendations": recs})

if __name__ == "__main__":
    app.run(debug=True)

#testy
# curl.exe "http://127.0.0.1:5000/api/recommend?title=Inception&top_n=2"