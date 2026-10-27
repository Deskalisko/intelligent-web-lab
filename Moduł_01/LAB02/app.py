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
    genre = request.args.get("genre", "").strip() or None

    data = recommend(title, top_n=n, genre=genre)
    if "suggestions" in data:
        return jsonify({
            "error": "nie ma takiego filmu",
            "suggestions": data["suggestions"]
        }), 404

    recs = data["recommendations"]
    return jsonify({
        "title": title,
        "genre": genre,
        "count": len(recs),
        "recommendations": recs
    })

    return jsonify({"title": title,"genre_filter": genre, "count": len(recs), "recommendations": recs})

if __name__ == "__main__":
    app.run(debug=True)

#testy
# curl.exe "http://127.0.0.1:5000/api/recommend?title=Inception&top_n=2"

#pasujace
# http://127.0.0.1:5000/api/recommend?title=Inception&top_n=3&genre=Drama
#http://127.0.0.1:5000/api/recommend?title=Inception&top_n=2&genre=Sci-Fi

#nie pasujace
# http://127.0.0.1:5000/api/recommend?title=Inception&top_n=3&genre=Comedy


#testy zadanie a
# curl.exe -i "http://127.0.0.1:5000/api/recommend?title=Inception&top_n=1"
# curl.exe -i "http://127.0.0.1:5000/api/recommend?title=Inception&top_n=10"
# curl.exe -i "http://127.0.0.1:5000/api/recommend?title=Inception&top_n=11"
# curl.exe -i "http://127.0.0.1:5000/api/recommend?title=Inception&top_n=0"
# curl.exe -i "http://127.0.0.1:5000/api/recommend?title=Inception&top_n=abc"

#testy zadanie b
# test literówki (404 NOT FOUNDT oraz sugestia Inception)
#curl.exe -i "http://127.0.0.1:5000/api/recommend?title=Incpetion"
# inna literówka
# curl.exe -i "http://127.0.0.1:5000/api/recommend?title=Interstel"