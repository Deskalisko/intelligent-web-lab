# Inteligentne Systemy Internetowe — Dokumentacja Projektu (EK_05)

Repozytorium zawiera realizację laboratoriów z przedmiotu **Inteligentne Systemy Internetowe**, podzielonych na dwa moduły tematyczne:
- **Moduł 1 (Laboratoria 1–3)**: Projektowanie API oraz systemy rekomendacji (Content-Based i Collaborative Filtering).
- **Moduł 2 (Laboratoria 4–5)**: Uczenie nienadzorowane i analiza tekstu w języku polskim (K-Means, DBSCAN, detekcja szumu).

---

## 🚀 Jak uruchomić (Instrukcja ogólna)

Wymagany jest język **Python** (w wersji 3.10 lub nowszej). Należy zainstalować niezbędne pakiety z pliku `requirements.txt`, a następnie w odpowiednim katalogu uruchomić skrypt laboratorium (np. `app.py`, `app2.py`):

```bash
# Instalacja zależności
pip install -r requirements.txt

# Uruchomienie aplikacji w wybranym folderze laboratorium
python app.py
```

> [!NOTE]
> Aplikacje korzystają z frameworka **Flask**, domyślnie nasłuchując na porcie **`5000`** (lub dedykowanych portach, np. **`5004`** dla Lab 4 oraz **`5005`** dla Lab 5).

---

# 📦 Moduł 1 (Laboratoria 1–3)

---

### 🔹 Lab 01: Podstawy API (Flask)

#### Co działa:
Aplikacja serwerowa realizująca podstawowe API typu **RESTful**. Umożliwia zarządzanie katalogiem produktów. Obsługuje:
- pobieranie całej listy produktów,
- filtrowanie wyników po maksymalnej cenie (`max_price`),
- wyszukiwanie produktu po identyfikatorze (`/api/products/<id>`),
- dodawanie nowych produktów (metoda `POST`) z rygorystyczną walidacją typu danych (zabezpieczenie przed wprowadzaniem `id` przez klienta czy tekstową wartością ceny).

#### Przykładowe żądania i odpowiedzi:

**1. Pobieranie produktów z filtrem ceny**
- **Żądanie:**  
  `GET /api/products?max_price=200`
- **Odpowiedź (`200 OK`):**  
  Zwraca listę produktów, których cena nie przekracza podanej wartości. W przypadku podania wartości niepoprawnej API zwraca błąd `400 Bad Request`.

```json
[
  {
    "cena": 129.0,
    "id": 2,
    "kategoria": "akcesoria",
    "nazwa": "Mysz bezprzewodowa",
    "opis": "Ciche przyciski, 4000 DPI"
  },
  {
    "cena": 199.0,
    "id": 5,
    "kategoria": "akcesoria",
    "nazwa": "Hub USB-C",
    "opis": "HDMI, 3x USB-A, czytnik SD"
  }
]
```

**2. Dodawanie nowego produktu**
- **Żądanie:**  
  `POST /api/products`
- **Body (`application/json`):**
  ```json
  {
    "nazwa": "Podkładka",
    "kategoria": "akcesoria",
    "cena": 49.99,
    "opis": "Rozmiar XL"
  }
  ```
- **Odpowiedź (`201 Created`):**  
  Zwraca nowo utworzony obiekt z wygenerowanym systemowo identyfikatorem:
  ```json
  {
    "cena": 49.99,
    "id": 6,
    "kategoria": "akcesoria",
    "nazwa": "Podkładka",
    "opis": "Rozmiar XL"
  }
  ```

---

### 🔹 Lab 02: API Rekomendacji – Content-Based Filtering

#### Co działa:
System rekomendacji bazujący na cechach elementów. 
- Analizuje opisy filmów (wektoryzacja **TF-IDF** z odrzuceniem *stop words*) i ich gatunki (**MultiLabelBinarizer**), łącząc je za pomocą **cosine similarity**.
- Posiada prosty interfejs webowy (`index.html`).
- Zwraca najlepiej dopasowane propozycje dla użytkownika, obsługuje opcjonalne filtrowanie po gatunku (`genre`) oraz elastyczne limitowanie wyników (`top_n`).
- W przypadku błędnego tytułu, API sugeruje poprawne nazwy przy użyciu biblioteki `difflib`.

#### Przykładowe żądania i odpowiedzi:

**Szukanie podobnych filmów z filtrem gatunku**
- **Żądanie:**  
  `GET /api/recommend?title=Inception&top_n=2&genre=Sci-Fi`
- **Odpowiedź (`200 OK`):**
  ```json
  {
    "count": 2,
    "genre": "Sci-Fi",
    "recommendations": [
      {
        "genres": "sci-fi|mystery",
        "rating": 8.0,
        "score": 0.091,
        "title": "Blade Runner 2049"
      }
    ],
    "title": "Inception"
  }
  ```

---

### 🔹 Lab 03: API Rekomendacji – Collaborative Filtering

#### Co działa:
System przewidujący preferencje bazujący na gustach społeczności.
- Wykorzystuje algorytm **k-NN** na centrowanych ocenach użytkowników.
- Endpoint `/api/recommend` szuka najbliższych „sąsiadów” o podobnym guście (parametr `k`) i na tej podstawie poleca najlepsze tytuły wraz z wyjaśnieniem (`because`).
- Dodatkowy endpoint `/api/users` udostępnia alfabetyczną listę wszystkich znanych użytkowników.
- W przypadku literówki, system zwraca propozycje z listy znanych użytkowników (kod `404 Not Found`).

#### Przykładowe żądania i odpowiedzi:

**Rekomendacje na podstawie sąsiadów (k-NN)**
- **Żądanie:**  
  `GET /api/recommend?user=Ania&k=3&top_n=1`
- **Odpowiedź (`200 OK`):**
  ```json
  {
    "count": 1,
    "k": 3,
    "recommendations": [
      {
        "because": [
          "Celina",
          "Jacek",
          "Kasia"
        ],
        "predicted": 4.31,
        "title": "Fight Club"
      }
    ],
    "user": "Ania"
  }
  ```

---

# 🧠 Moduł 2 (Laboratoria 4–5)

---

### 🔹 Lab 04: Grupowanie tekstów (K-Means)

#### Co działa:
System analizujący teksty polskojęzyczne i dzielący je na grupy tematyczne za pomocą algorytmu **K-Means** bazującego na macierzy **TF-IDF**.
- API udostępnia endpoint pokazujący dopasowane grupy (klastry), zwracając dla każdego z nich jego wielkość, najlepiej dopasowane słowa kluczowe (wyznaczone po parametrach centroidu) oraz listę przypisanych artykułów.
- Dodatkowy endpoint `/api/elbow` zwraca analizę **metody łokcia** dla wartości $k$ od 2 do 8, co ułatwia decyzję o docelowej liczbie klastrów.

> [!TIP]
> **Uwaga badawcza:** Optymalny podział danych uzyskano dla **`k=6`** oraz ograniczeniu do 100 najistotniejszych cech (`max_features=100`), co potwierdzono wskaźnikiem **ARI** (*Adjusted Rand Index*) wynoszącym **`0.814`**, idealnie separując artykuły m.in. o rolnictwie i technologii.

#### Przykładowe żądania i odpowiedzi:

**1. Pobranie informacji o wygenerowanym klastrze**
- **Żądanie:**  
  `GET /api/clusters/0` *(dla k=6)*
- **Odpowiedź (`200 OK`):**
  ```json
  {
    "cluster_id": 0,
    "count": 9,
    "keywords": [
      "trening",
      "wynik",
      "zawodników",
      "zawodnicy"
    ],
    "articles": [
      {
        "id": 12,
        "title": "...",
        "text": "..."
      }
    ]
  }
  ```

**2. Metoda Łokcia (Elbow)**
- **Żądanie:**  
  `GET /api/elbow`
- **Odpowiedź (`200 OK`):**
  ```json
  [
    {
      "inertia": 34.352,
      "k": 2
    },
    {
      "inertia": 31.841,
      "k": 3
    }
  ]
  ```

---

### 🔹 Lab 05: Wykrywanie szumu w tekstach (DBSCAN)

#### Co działa:
Rozwinięcie metod analizy tekstu z użyciem algorytmu **DBSCAN** opartego na macierzy odległości kosinusowych, w celu wykrywania „szumu” oraz grup o różnych gęstościach, w przeciwieństwie do sztywnego podziału algorytmu K-Means.
- Aplikacja udostępnia API do ewaluacji modeli: porównuje **K-Means**, **DBSCAN** i **AgglomerativeClustering** pod kątem liczby uzyskanych grup, zidentyfikowanego szumu oraz miary **Silhouette**.
- Dodatkowo API posiada endpoint klasyfikujący dowolny przesłany tekst do istniejących rdzeni klastrów, a w przypadku odrzucenia (przekroczenie promienia `eps`) zwraca powód odrzucenia, taki jak brak wspólnego słownika (`out_of_vocabulary`) czy zbyt dużą odległość kosinusową.

#### Przykładowe żądania i odpowiedzi:

**1. Porównanie metod grupowania**
- **Żądanie:**  
  `GET /api/compare`
- **Odpowiedź (`200 OK`):**  
  Zwraca zestawienie (z wykorzystaniem wskaźnika silhouette) zawierające czas wykonania, liczbę punktów szumu i ilość klastrów dla wszystkich 3 metod.
  ```json
  {
    "eps": 0.74,
    "min_samples": 3,
    "results": [
      {
        "algorithm": "K-Means",
        "clusters": 5,
        "elapsed_ms": 14.2,
        "noise": 0,
        "scored_articles": 52,
        "silhouette_cosine": 0.156
      },
      {
        "algorithm": "DBSCAN",
        "clusters": 7,
        "elapsed_ms": 1.8,
        "noise": 4,
        "scored_articles": 48,
        "silhouette_cosine": 0.220
      },
      {
        "algorithm": "Agglomerative",
        "clusters": 5,
        "elapsed_ms": 3.1,
        "noise": 0,
        "scored_articles": 52,
        "silhouette_cosine": 0.165
      }
    ]
  }
  ```

**2. Przypisanie nowego tekstu i detekcja szumu**
- **Żądanie:**  
  `POST /api/cluster/assign`
- **Body (`application/json`):**
  ```json
  {
    "text": "Całkiem nowy artykuł niepowiązany z resztą"
  }
  ```
- **Odpowiedź (`200 OK`):**
  ```json
  {
    "cluster_id": -1,
    "distance_to_core": 0.812,
    "noise": true,
    "rule": "nearest_core_within_eps"
  }
  ```
