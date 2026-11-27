"""Testy "na sucho" kodu z Lab 1. Uruchom w folderze lab1: python test_lab01.py"""
import importlib.util
from pathlib import Path

HERE = Path(__file__).parent


def load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check(client, method, url, expected_status):
    resp = getattr(client, method)(url)
    assert resp.status_code == expected_status, (
        f"{method.upper()} {url} -> {resp.status_code}, oczekiwano {expected_status}"
    )
    return resp


def test_starter(client):
    r = check(client, "get", "/api/health", 200)
    assert r.get_json() == {"status": "ok"}, "health: zla tresc"
    r = check(client, "get", "/api/products", 200)
    data = r.get_json()
    assert isinstance(data, list) and len(data) == 5, "products: oczekiwano 5 produktow"
    for p in data:
        assert {"id", "nazwa", "kategoria", "cena", "opis"} <= set(p), f"produkt bez wszystkich pol: {p}"


def test_solution(client):
    test_starter(client)
    r = check(client, "get", "/api/products/3", 200)
    assert r.get_json()["id"] == 3, "produkt po id: zly obiekt"
    r = check(client, "get", "/api/products/99", 404)
    assert r.get_json() == {"error": "not found"}, "404: zla tresc komunikatu"
    check(client, "get", "/api/products/abc", 404)  # konwerter <int:> odrzuca nieliczby
    r = client.post("/api/products", json={
        "nazwa": "Kabel HDMI", "kategoria": "akcesoria", "cena": 49.00, "opis": "2 m",
    })
    assert r.status_code == 201, f"POST -> {r.status_code}, oczekiwano 201"
    assert r.get_json()["id"] == 6, "POST: nowe id powinno byc 6"
    r = check(client, "get", "/api/products/6", 200)
    assert r.get_json()["nazwa"] == "Kabel HDMI", "POST: produkt nie zapisal sie"
    r = check(client, "get", "/api/products?max_price=200", 200)
    assert all(p["cena"] <= 200 for p in r.get_json()) and len(r.get_json()) == 3
    for limit in ("abc", "", "-1", "nan", "inf"):
        check(client, "get", f"/api/products?max_price={limit}", 400)
    before = client.get("/api/products").get_json()
    valid = {"nazwa": "Kabel", "kategoria": "akcesoria", "cena": 10, "opis": "2 m"}
    for data in ([], {}, None, {**valid, "id": 1}, {**valid, "cena": -1},
                 {**valid, "cena": True}, {**valid, "cena": "10"},
                 {**valid, "cena": float("nan")}, {**valid, "nazwa": " "}):
        response = client.post("/api/products", json=data)
        assert response.status_code == 400 and response.is_json, data
    response = client.post("/api/products", data="{", content_type="application/json")
    assert response.status_code == 400 and response.is_json
    assert client.get("/api/products").get_json() == before, "Błędny POST zmienił katalog"


if __name__ == "__main__":
    starter = load_module("app", "app.py")
    test_starter(starter.app.test_client())
    print("[OK] app.py (starter): /api/health, /api/products")

    solution = load_module("rozwiazanie", "rozwiazanie.py")
    test_solution(solution.app.test_client())
    print("[OK] rozwiazanie.py: produkt po id, 404, konwerter int, POST 201")
    print("Wszystkie testy przeszly.")
