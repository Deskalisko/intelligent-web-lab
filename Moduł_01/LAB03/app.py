from flask import Flask, jsonify, request
from recommender import matrix, recommend

app = Flask(__name__)


@app.route("/api/recommend")
def api_recommend():
    user = request.args.get("user", "").strip()
    if not user:
        return jsonify({"error": "podaj parametr ?user=..."}), 400

    n = request.args.get("top_n", type=int) if "top_n" in request.args else 5
    if n is None or not 1 <= n <= 10:
        return jsonify({"error": "top_n musi byc z zakresu 1-10"}), 400

    k = request.args.get("k", type=int) if "k" in request.args else 3
    if k is None or not 1 <= k <= 11:
        return jsonify({"error": "k musi byc z zakresu 1-11"}), 400

    data = recommend(user, top_n=n, k=k)
    if "suggestions" in data:
        return (
            jsonify(
                {
                    "error": "nie znam takiego uzytkownika",
                    "suggestions": data["suggestions"],
                    "known_users": sorted(matrix.index.tolist()),
                }
            ),
            404,
        )

    recs = data["recommendations"]
    return jsonify(
        {
            "user": user,
            "k": k,
            "count": len(recs),
            "recommendations": recs,
        }
    )
if __name__ == "__main__":
    app.run(debug=True)

