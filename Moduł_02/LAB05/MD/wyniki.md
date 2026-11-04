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

<br>

# Zadanie A - Porównanie wartości `EPS` przy `MIN_SAMPLES = 3`

W celu sprawdzenia wpływu parametru `EPS` na działanie algorytmu DBSCAN wykonaliśmy trzy pomiary dla wartości:

```text
EPS = 0.70
EPS = 0.74
EPS = 0.79
```

przy stałej wartości:

```text
MIN_SAMPLES = 3
```

## Wyniki

| EPS  | Liczba grup | Liczba artykułów oznaczonych jako szum | Ocenione artykuły | Silhouette |
| ---- | ----------- | -------------------------------------- | ----------------- | ---------- |
| 0.70 | 7           | 8                                      | 44                | 0.241      |
| 0.74 | 7           | 4                                      | 48                | 0.220      |
| 0.79 | 4           | 2                                      | 50                | 0.140      |

---

## Artykuły oznaczone jako szum

### EPS = 0.70

```text
Koncert orkiestry w teatrze
Muzyczny debiut zespołu
Las wraca po pożarze
Retencja wody w miastach
Odpady trafiają do recyklingu
Temperatura jezior rośnie
Nowa odmiana pszenicy odporna na suszę
Badania nad odpornością kukurydzy na upały
```

Przy najmniejszym promieniu algorytm miał największe problemy z odnalezieniem odpowiedniej liczby sąsiadów, dlatego aż 8 artykułów zostało oznaczonych jako szum.

---

### EPS = 0.74

```text
Retencja wody w miastach
Temperatura jezior rośnie
Nowa odmiana pszenicy odporna na suszę
Badania nad odpornością kukurydzy na upały
```

Po zwiększeniu promienia liczba artykułów oznaczonych jako szum zmniejszyła się z 8 do 4. Część artykułów uzyskała wystarczającą liczbę sąsiadów, aby zostać przypisana do istniejących grup.

---

### EPS = 0.79

```text
Retencja wody w miastach
Temperatura jezior rośnie
```

Przy największym promieniu tylko 2 artykuły pozostały szumem. Jednocześnie liczba grup spadła do 4, ponieważ część wcześniej oddzielnych klastrów została połączona.

---

<br>

# Zadanie B - Wybór metody dla redakcji

### Porównanie metod

| Algorytm      | Grupy | Szum | Silhouette cosine | Ocenione artykuły |
| ------------- | ----- | ---- | ----------------- | ----------------- |
| K-Means       | 5     | 0    | 0.156             | 52                |
| DBSCAN        | 7     | 4    | 0.220             | 48                |
| Agglomerative | 5     | 0    | 0.165             | 52                |

---

### Wniosek

Wybraliśmy **DBSCAN**.

Osiągnął najwyższą wartość współczynnika silhouette (`0.220`), co oznacza lepsze rozdzielenie grup niż w przypadku K-Means (`0.156`) oraz Agglomerative (`0.165`).

Dodatkowo DBSCAN potrafi wykrywać artykuły, które nie pasują do żadnej grupy i oznaczać je jako szum. Przykładem jest artykuł:

```text
Temperatura jezior rośnie
```

Artykuł ten został oznaczony jako szum (`-1`), ponieważ nie miał wystarczającej liczby podobnych sąsiadów. Dzięki temu redakcja może łatwo zauważyć nietypowe lub trudne do zaklasyfikowania teksty zamiast przypisywać je na siłę do jednej z istniejących kategorii.

Współczynnik silhouette został obliczony dla:

```text
48 artykułów
```

ponieważ 4 artykuły zostały oznaczone przez DBSCAN jako szum i nie zostały uwzględnione w obliczeniach.

---

<br>
