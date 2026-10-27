# API Rekomendacji (Lab 02 i 03)

Projekt API w Pythonie (Flask) realizujący dwa systemy rekomendacji filmowych. Zwraca wyniki w formacie JSON.

## Co robi ten moduł

* Content-Based Filtering (Lab 02): Analizuje opisy filmów i na podstawie ich podobieństwa tematycznego (TF-IDF i cosine similarity) znajduje tytuły o zbliżonej treści.
* Collaborative Filtering (Lab 03): Porównuje oceny wystawiane przez użytkowników (k-NN na ocenach centrowanych). Znajduje "sąsiadów" o podobnym guście i przewiduje, jak użytkownik oceniłby nieznany mu film.

## Jak uruchomić

Zainstaluj wymagane biblioteki i uruchom plik główny:

pip install -r requirements.txt
python app.py

Serwer będzie dostępny pod adresem: http://127.0.0.1:5000

## Przykłady zapytań API

### 1. Collaborative Filtering (rekomendacje po ocenach ludzi)

Znajduje 3 najbliższych sąsiadów dla podanej osoby.

Żądanie: GET /api/recommend?user=Ania&k=3

Przykładowa odpowiedź:
{
  "user": "Ania",
  "k": 3,
  "count": 1,
  "recommendations": [
    {
      "title": "Fight Club",
      "predicted": 4.31,
      "because": [
        "Celina",
        "Jacek",
        "Kasia"
      ]
    }
  ]
}

### 2. Content-Based (rekomendacje po opisie filmu)

Znajduje podaną liczbę (top_n) filmów podobnych treściowo do wskazanego.

Żądanie: GET /api/recommend?title=Inception&top_n=2

Przykładowa odpowiedź:
{
  "title": "Inception",
  "count": 2,
  "recommendations": [
    {
      "title": "Blade Runner 2049",
      "genres": "sci-fi|mystery",
      "rating": 8.0,
      "score": 0.091
    },
    {
      "title": "The Dark Knight",
      "genres": "action|crime",
      "rating": 9.0,
      "score": 0.063
    }
  ]
}