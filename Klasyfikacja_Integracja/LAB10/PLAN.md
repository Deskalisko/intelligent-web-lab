# PLAN.md: projekt inteligentnego systemu internetowego

Dokument oddawany razem z kodem na checkpoint **CP-3** (Lab 10). Wpisz decyzje zespołu w pola `[…]`. Podczas obrony pokaż, który wynik testu uzasadnia każdą decyzję.

## 1. Cel i zakres

System odpowiada na cztery pytania klienta w jednym API:

1. „Co jeszcze obejrzę?” rekomendacje content-based, czyli na podstawie opisu (Lab 2),
2. „Co polubili podobni do mnie?” rekomendacje collaborative, czyli na podstawie ocen (Lab 3),
3. „Gdzie pisaliśmy o X?” wyszukiwanie z rankingiem BM25 (Lab 6),
4. „Jaki sentyment ma ta opinia?” klasyfikacja tekstu (Lab 8).

## 2. Schemat blokowy

```text
KLIENT (przeglądarka / curl)
   │  żądanie HTTP
   ▼
API · Flask  (lab10/app.py)
   │  walidacja wejścia (400/404/413)
   ├─► /api/recommend/content ─► TF-IDF + cosine ─► movies.csv        (Lab 2)
   ├─► /api/recommend/collaborative ─► sąsiedzi + średnia ważona ─► ratings.csv (Lab 3)
   ├─► /api/search ─► indeks odwrócony + BM25 ─► articles.csv         (Lab 6)
   └─► /api/feedback ─► TF-IDF + klasyfikator ─► etykieta             (Lab 8)
   │
   ▼
JSON (query/results · label/probability_estimate · error)
```

## 3. Harmonogram

| Kiedy | Kamień milowy | Efekt w repo |
|---|---|---|
| Lab 1 | API i repozytorium | `app.py`, `.gitignore`, pierwszy commit |
| Lab 2-3 (**CP-1**) | rekomendacje | `recommender.py`, endpointy rekomendacji |
| Lab 4-5 | klastrowanie treści | `cluster.py`, `compare.py`, raport elbow/silhouette (dobór liczby klastrów) |
| Lab 6-7 (**CP-2**) | wyszukiwanie i ranking | `search_engine.py`, `search.py`, raport porównawczy 3 silników |
| Lab 8-9 | klasyfikacja | `classifier.py`, `compare.py`, macierze pomyłek, porównanie modeli |
| Lab 10 (**CP-3**) | integracja | jeden serwis + ten dokument |

## 4. Podział ról w parze

- Osoba A: […] (np. warstwa API, walidacje, integracja modułów)
- Osoba B: […] (np. modele ML, metryki, dokumentacja)

Po każdej części zadania zamieńcie się rolami. Partner sprawdza zmianę i zapisuje wynik próby.

### Próba odbiorowa własnej zmiany

- Co zmieniamy: […]
- Jakie dane wpisuje osoba sprawdzająca: […]
- Oczekiwana odpowiedź: […]
- Wynik próby i uwagi drugiej pary: […]

Przykład poprawnej próby: `GET /api/recommend/content?title=Inception&top_n=3` zwraca status 200 i listę rekomendacji.

## 5. Wybory modeli i uzasadnienie

| Decyzja | Wybór | Uzasadnienie (metryka) |
|---|---|---|
| Reprezentacja tekstu | TF-IDF | […] |
| Rekomendacje | content-based + collaborative | […] |
| Wyszukiwanie | BM25 (własny) vs semantyka | […] |
| Klasyfikacja | MultinomialNB / LogisticRegression | macro F1 = […] |

## 6. Ograniczenia i ryzyka

- dane ćwiczeniowe są małe i syntetyczne (24 filmy, 40 artykułów, 54 opinie, 40 wiadomości), więc nie dowodzą działania produkcyjnego,
- brak warstwy produkcyjnej: cache, kolejka zadań, monitoring, procesy robocze WSGI,
- zimny start (cold start) w collaborative dla nowych użytkowników i filmów bez ocen; nowe dokumenty wymagają przebudowy indeksu,
- dryf danych: opinie zmieniają język, indeks trzeba przebudowywać.

## 7. Co dalej

- [ ] własne dane testowe (nowe źródło opinii, nowe produkty),
- [ ] pomiar pełnej ścieżki żądania (reprezentacja + predykcja) na rozgrzanych modelach,
- [ ] test A/B lub offline na odłożonym zbiorze z ustaloną metryką biznesową.
