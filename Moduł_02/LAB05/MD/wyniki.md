# LAB 05 - DBSCAN, K-Means i Agglomerative

> Wykorzystaliśmy rozszerzony zbiór `articles.csv` z poprzedniego zadania, ktory zawiera 52 artykuły (dodatkowe teksty związane między innymi z rolnictwem).

---

# Wyniki dla EPS = 0.74 i MIN_SAMPLES = 3

```text
{'algorithm': 'K-Means', 'clusters': 5, 'noise': 0, 'scored_articles': 52, 'silhouette_cosine': 0.156}
{'algorithm': 'DBSCAN', 'clusters': 7, 'noise': 4, 'scored_articles': 48, 'silhouette_cosine': 0.220}
{'algorithm': 'Agglomerative', 'clusters': 5, 'noise': 0, 'scored_articles': 52, 'silhouette_cosine': 0.165}
```

Artykuły oznaczone jako szum:

```text
Retencja wody w miastach
Temperatura jezior rośnie
Nowa odmiana pszenicy odporna na suszę
Badania nad odpornością kukurydzy na upały
```

### Komentarz

Przy tych ustawieniach DBSCAN utworzył 7 grup oraz oznaczył 4 artykuły jako szum. Były to głównie artykuły związane ze środowiskiem i rolnictwem, które okazały się zbyt odległe od pozostałych tekstów. Współczynnik silhouette był najwyższy właśnie dla DBSCAN, co oznacza najlepsze rozdzielenie grup.

---

# Wyniki dla EPS = 0.70 i MIN_SAMPLES = 4

```text
{'algorithm': 'DBSCAN', 'clusters': 5, 'noise': 23, 'scored_articles': 29, 'silhouette_cosine': 0.256}
```

Liczba artykułów oznaczonych jako szum: `23`

### Komentarz

Zmniejszenie wartości `EPS` oraz zwiększenie `MIN_SAMPLES` spowodowało bardzo restrykcyjne warunki tworzenia klastrów. W efekcie aż 23 artykuły zostały uznane za szum. Mimo wysokiej wartości silhouette taki wynik nie jest praktyczny, ponieważ prawie połowa zbioru została odrzucona.

---

# Wyniki dla EPS = 0.75 i MIN_SAMPLES = 1

```text
{'algorithm': 'DBSCAN', 'clusters': 9, 'noise': 0, 'scored_articles': 52, 'silhouette_cosine': 0.227}
```

### Komentarz

Przy `MIN_SAMPLES = 1` każdy punkt może samodzielnie stać się rdzeniem. W praktyce powoduje to całkowite zniknięcie szumu i powstanie bardzo dużej liczby małych grup.

---

# Początkowe wyniki dla DBSCAN

| EPS  | MIN_SAMPLES | Grupy | Szum | Ocenione artykuły |
| ---- | ----------- | ----- | ---- | ----------------- |
| 0.70 | 4           | 5     | 23   | 29                |
| 0.74 | 3           | 7     | 4    | 48                |
| 0.74 | 2           | 9     | 0    | 52                |
| 0.75 | 1           | 9     | 0    | 52                |
| 0.75 | 3           | 7     | 4    | 48                |

---

# Działanie parametrów

### Wpływ EPS

- mniejszy EPS → więcej szumu
- większy EPS → mniej szumu
- zbyt duży EPS → klastry zaczynają się łączyć

### Wpływ MIN_SAMPLES

- mniejszy MIN_SAMPLES → łatwiej tworzyć grupy
- większy MIN_SAMPLES → trudniej tworzyć grupy
- zbyt duży MIN_SAMPLES → dużo punktów zostaje oznaczonych jako szum

---

# Przykłady odpowiedzi API

## GET /api/compare

Odpowiedź:

```json
{
  "eps": 0.74,
  "min_samples": 3,
  "results": [
    {
      "algorithm": "K-Means",
      "clusters": 5,
      "noise": 0,
      "scored_articles": 52,
      "silhouette_cosine": 0.156
    },
    {
      "algorithm": "DBSCAN",
      "clusters": 7,
      "noise": 4,
      "scored_articles": 48,
      "silhouette_cosine": 0.22
    },
    {
      "algorithm": "Agglomerative",
      "clusters": 5,
      "noise": 0,
      "scored_articles": 52,
      "silhouette_cosine": 0.165
    }
  ]
}
```

Endpoint zwraca porównanie wszystkich trzech metod grupowania wraz z liczbą klastrów, liczbą artykułów oznaczonych jako szum oraz wartością współczynnika silhouette.

---

## GET /api/noise

Odpowiedź:

```json
[
  {
    "id": 36,
    "title": "Retencja wody w miastach"
  },
  {
    "id": 40,
    "title": "Temperatura jezior rośnie"
  },
  {
    "id": 47,
    "title": "Nowa odmiana pszenicy odporna na suszę"
  },
  {
    "id": 52,
    "title": "Badania nad odpornością kukurydzy na upały"
  }
]
```

Endpoint zwraca listę artykułów, które DBSCAN uznał za szum przy aktualnych ustawieniach.

---

## POST /api/cluster/assign

Podczas testów próba wysłania tekstu przez curl zakończyła się błędem składni polecenia PowerShell, dlatego serwer odczytał pustą wartość pola `text`.

Otrzymana odpowiedź:

```json
{
  "error": "podaj niepusty tekst w polu text"
}
```

---

## Pusty tekst

Kod odpowiedzi:

```text
HTTP 400 BAD REQUEST
```

Treść odpowiedzi:

```json
{
  "error": "podaj niepusty tekst w polu text"
}
```

Serwer poprawnie odrzuca puste dane wejściowe i zwraca kod błędu 400.

---

# Podsumowanie dotychczasowych obserwacji

Najwyższą wartość współczynnika silhouette uzyskał DBSCAN. Algorytm ten najlepiej rozdzielał grupy artykułów, ale jednocześnie potrafił oznaczać część tekstów jako szum. K-Means i Agglomerative przypisywały każdy artykuł do jakiegoś klastra, jednak uzyskiwały gorsze wyniki silhouette.
