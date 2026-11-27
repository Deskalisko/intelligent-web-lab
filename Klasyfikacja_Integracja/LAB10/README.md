# Inteligentny system internetowy: projekt zaliczeniowy (Lab 10)

Jeden serwis Flask, który spina moduły z wcześniejszych laboratoriów za jednym interfejsem:

| Moduł | Skąd | Endpoint |
|---|---|---|
| Rekomendacje content-based (na podstawie opisu filmu) | Lab 2 (TF-IDF + cosine) | `GET /api/recommend/content?title=Inception&top_n=3` |
| Rekomendacje collaborative (na podstawie ocen użytkowników) | Lab 3 (sąsiedzi, ważona średnia) | `GET /api/recommend/collaborative?user=Ania&top_n=3` |
| Wyszukiwanie | Lab 6 (indeks odwrócony + BM25) | `GET /api/search?q=procesor&top_n=3` |
| Klasyfikacja opinii | Lab 8 (TF-IDF + regresja logistyczna) | `POST /api/feedback` (JSON `{"text": "..."}`) |
| Katalog danych | Lab 2 / 3 | `GET /api/catalog` |
| Stan systemu | bezpośrednio w aplikacji | `GET /api/health` |

## Uruchomienie

```bash
cd lab10
py -m venv venv
venv\Scripts\activate           # Windows CMD
pip install -r requirements.txt
py app.py                        # → http://127.0.0.1:5010/
```

W PowerShellu aktywacja bywa blokowana przez politykę wykonywania skryptów. Wtedy użyj CMD albo uruchamiaj Pythona bez aktywacji: `venv\Scripts\python -m pip install -r requirements.txt` i `venv\Scripts\python app.py`.

Strony pomocnicze: `/project` (ten plik) i `/plan` (`PLAN.md`).

Cały kurs uruchomisz poleceniem `py app.py` z katalogu głównego repozytorium.
Otwórz wtedy `http://127.0.0.1:8000/`. Lab 10 działa pod `/lab10/index.html`,
a jego API pod `/lab10/api/`. Adresy powyżej dotyczą osobnego serwera Lab 10 na porcie 5010.

## Kody błędów

- brak lub pusty parametr → `400`
- zły JSON albo brak pola `text` → `400`
- `top_n` poza zakresem 1-10 → `400`
- `q` w `/api/search` dłuższe niż 200 znaków → `400`
- nieznany tytuł / użytkownik → `404`
- `text` w `/api/feedback` dłuższy niż 4000 znaków → `413`

## Weryfikacja

Z katalogu głównego repo:

```bash
py verify_labs.py
```

Skrypt sprawdza API wszystkich dziesięciu laboratoriów (łącznie z tym systemem) bez otwierania przeglądarki. Brak pakietu, np. torch w Lab 9, kończy się pominięciem z komunikatem, nie błędem.
