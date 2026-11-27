from flask import Flask, jsonify, request
#request - do odczytu danych z zewnątrz
import math #math do maxprice'a

app = Flask(__name__)

PRODUCTS = [
    {"id": 1, "nazwa": "Klawiatura mechaniczna", "kategoria": "akcesoria",
     "cena": 349.99, "opis": "Przełączniki hot-swap, podświetlenie RGB"},
    {"id": 2, "nazwa": "Mysz bezprzewodowa", "kategoria": "akcesoria",
     "cena": 129.00, "opis": "Ciche przyciski, 4000 DPI"},
    {"id": 3, "nazwa": "Monitor 27 cali", "kategoria": "monitory",
     "cena": 1099.00, "opis": "Matryca IPS, 144 Hz"},
    {"id": 4, "nazwa": "Słuchawki nauszne", "kategoria": "audio",
     "cena": 449.00, "opis": "ANC, 40 h pracy na baterii"},
    {"id": 5, "nazwa": "Hub USB-C", "kategoria": "akcesoria",
     "cena": 199.00, "opis": "HDMI, 3x USB-A, czytnik SD"},
]

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/api/products")
def products():
    if "max_price" in request.args:
        max_price = request.args.get("max_price", type=float)

        if (max_price is None or
            max_price < 0 or
            math.isnan(max_price) or #nan not a number
            math.isinf(max_price)): #infinity
            return jsonify({"error": "invalid max_price"}), 400

        filtracja = []
        for produkt in PRODUCTS:
            if produkt["cena"] <= max_price:
                filtracja.append(produkt)
        return jsonify(filtracja)

    return jsonify(PRODUCTS)

@app.route("/api/products/<int:id>")
def pobierz_produkt(id):
    for produkt in PRODUCTS:
        if produkt["id"] == id:
            return jsonify(produkt)
    return jsonify({"error": "not found"}), 404 #jak nie będzie, zwróci że nie znaleziono

#nowe produkty
@app.route("/api/products", methods=["POST"])
def dodaj_produkt():
    dane = request.get_json(silent=True) #wylacza blad json przy złym jsonie np brakujący "" lub przecinek

    if not isinstance(dane, dict):  # czy na pewno przesłano obiekt dict a nie np liste
        return jsonify({"error": "invalid json or body format"}), 400

    if "id" in dane: #niepotrzebne nam id, nie chcemy go przesyłac ma sie tworzyc samo
        return jsonify({"error": "id nie moze wprowadzac klient "}), 400

    nazwa = dane.get("nazwa")
    kategoria = dane.get("kategoria")
    opis = dane.get("opis")
    cena = dane.get("cena")

    #pola nie moga byc puste i musza byc stringiem
    if not isinstance(nazwa, str) or not nazwa.strip():
        return jsonify({"error": "invalid nazwa"}), 400
    if not isinstance(kategoria, str) or not kategoria.strip():
        return jsonify({"error": "invalid kategoria"}), 400
    if not isinstance(opis, str) or not opis.strip():
        return jsonify({"error": "invalid opis"}), 400

    if(type(cena) not in (int, float) or
        cena < 0 or
        not math.isfinite(cena)):
        return jsonify({"error": "invalid cena"}), 400

    if PRODUCTS:
        nowe_id = len(PRODUCTS) + 1
    else:
        nowe_id = 1

    nowy_produkt = {
        "id": nowe_id,
        "nazwa" : nazwa.strip(),#strip do usuniecia spacji i białych znakow
        "kategoria": kategoria.strip(),
        "cena": float(cena),
        "opis": opis.strip()
    }

    PRODUCTS.append(nowy_produkt)
    return jsonify(nowy_produkt), 201

#aby dodać coś do testu
# Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/products" -Method Post -ContentType "application/json" -Body '{"nazwa": "Podkładka pod mysz", "kategoria": "akcesoria", "cena": 49.99, "opis": "Rozmiar XL"}'

#błedne
#cena jako napis
# Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/products" -Method Post -ContentType "application/json" -Body '{"nazwa": "Test", "kategoria": "kat", "cena": "100", "opis": "opis"}'

# id od klienta
# Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/products" -Method Post -ContentType "application/json" -Body '{"id": 10, "nazwa": "Test", "kategoria": "kat", "cena": 100, "opis": "opis"}'

if __name__ == "__main__":
    app.run(debug=True)