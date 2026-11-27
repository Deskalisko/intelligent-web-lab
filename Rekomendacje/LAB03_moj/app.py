from flask import Flask, jsonify, request
from recommender import matrix, recommend

# utworzenie instancji aplikacji flask
app = Flask(__name__)

@app.route("/api/users")
def api_users():
    # wyciągnięcie unikalnych imion z indeksu macierzy i posortowanie ich
    users_list = sorted(matrix.index.tolist())

    # zwrócenie listy w formacie json wraz z ich łączną liczbą (count)
    return jsonify({"count": len(users_list), "users": users_list})

# dekorator wskazujący ścieżkę endpointu api (metoda get)
@app.route("/api/recommend")
def api_recommend():
    # pobranie nazwy użytkownika z parametru zapytania URL (?user=...) i usunięcie białych znaków (.strip)
    user = request.args.get("user", "").strip()

    # walidacja parametru user: jeśli nie podano użytkownika, zwracamy kod błędu 400 bad request
    if not user:
        return jsonify({"error": "podaj parametr ?user=..."}), 400

    # pobranie i walidacja parametru top_n (domyślnie 5, zakres 1-10)
    top_n = request.args.get("top_n", type=int) if "top_n" in request.args else 5
    if top_n is None or not 1 <= top_n <= 10:
        return jsonify({"error": "top_n musi byc z zakresu 1-10"}), 400

    # pobranie i walidacja parametru k - liczba sąsiadów (domyślnie 3, zakres 1-11)
    k = request.args.get("k", type=int) if "k" in request.args else 3
    if k is None or not 1 <= k <= 11:
        return jsonify({"error": "k musi byc z zakresu 1-11"}), 400

    # wywołanie funkcji rekomendującej z recommender.py z podanymi parametrami
    recs = recommend(user, top_n=top_n, k=k)

    # obsługa nieznanego użytkownika: funkcja recommend zwraca None jeśli user nie istnieje w macierzy
    # zwracamy kod błędu 404 not found wraz z posortowaną listą wszystkich znanych użytkowników z macierzy
    if recs is None:
        return (
            jsonify(
                {
                    "error": "nie znam takiego uzytkownika",
                    "known_users": sorted(matrix.index.tolist()),
                }
            ),
            404,
        )

    # sukces: zwrócenie odpowiedzi json z wyliczonymi rekomendacjami (kod 200 ok)
    return jsonify(
        {
            "user": user,
            "k": k,
            "count": len(recs),
            "recommendations": recs,
        }
    )


# uruchomienie serwera deweloperskiego flaska (tylko przy bezpośrednim uruchomieniu pliku)
if __name__ == "__main__":
    app.run(debug=True)