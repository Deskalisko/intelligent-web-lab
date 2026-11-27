from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

# wczytanie pliku csv z ocenami (kolumny: user, title, rating)
df = pd.read_csv("ratings.csv")

# przekształcenie tabeli na macierz dwuwymiarową:
# - wiersze (index)="user" -> unikalni użytkownicy (12 osób)
# - kolumny (columns)="title" -> unikalne filmy (24 pozycje)
# - wartości (values)="rating" -> oceny (brak oceny = NaN)
# pivot tworzy wektory gustu w jednej operacji zamiast powolnej pętli.
# macierz pozwala jednym działaniem zmierzyć podobieństwo całych profili
matrix = df.pivot_table(index="user", columns="title", values="rating")

# SŁOWNIK POJĘĆ OSI (AXIS):
# axis=1: operacja POZIOMO (wzdłuż wierszy). liczy średnią dla każdego użytkownika z osobna
# axis=0: operacja PIONOWO (wzdłuż kolumn). dopasowuje odejmowanie do wierszy użytkowników

# wyliczenie średniej oceny dla każdego użytkownika z osobna (axis=1 po wierszach)
means = matrix.mean(axis=1)

# centrowanie ocen i wypełnianie braków:
# sub() odejmuje wartości. parametr axis=0 oznacza dopasowanie PIONOWE do wierszy:
#   - odejmuje średnią Ani od wiersza Ani, średnią Bartka od wiersza Bartka
#   - zamienia gwiazdki na odchylenia:
#       +1.0 -> użytkownik ocenił film wyżej niż swoją średnią (podobał mu się)
#       -1.0 -> użytkownik ocenił film niżej niż swoją średnią (nie podobał mu się)
# fillna(0) zastępuje braki danych (NaN) zerem: wskazuje neutralne odchylenie (średnia usera)
centered = matrix.sub(means, axis=0).fillna(0)

# podobieństwo cosinusowe na wyśrodkowanych wektorach odchyleń:
# cosine_similarity() przyjmuje wyśrodkowaną macierz 'centered' i wylicza kąt między wektorami
# mierzy zgodność odchyleń od średnich dla każdej pary użytkowników
# wynik mieści się w przedziale od -1.0 (zupełnie odwrotny gust) do +1.0 (identyczny gust)
sim = pd.DataFrame(
    cosine_similarity(centered), index=matrix.index, columns=matrix.index
)


# definicja funkcji recommend: user (dla kogo polecamy), top_n (ile filmów zwrócić), k (ilu sąsiadów)
def recommend(user, top_n=5, k=3):
    # sprawdzenie czy użytkownik istnieje w macierzy
    if user not in matrix.index:
        return None

    # pobranie top-k najbardziej podobnych osób (sąsiadów) z wykluczeniem samego siebie (.drop):
    # - sim[user]: wyciąga kolumnę wartości podobieństwa dla wybranego usera
    # - .drop(user): usuwa samego usera, żebysmy nie rekomendowali na podstawie samego siebie
    # - .sort_values(ascending=False): sortuje malejąco (od najbardziej podobnych +1.0 do -1.0)
    # - .head(k): wybiera pierwszych k sąsiadów z samej góry
    neighbors = sim[user].drop(user).sort_values(ascending=False).head(k)

    # słownik na przewidywane oceny nieocenionych filmów (klucz: tytuł filmu, wartość: ocena)
    scores = {}

    # pętla po wszystkich filmach w macierzy (matrix.columns to lista wszystkich 24 tytułów)
    for movie in matrix.columns:
        # sprawdzamy czy film był już oceniony przez wybranego użytkownika:
        # - matrix.loc[user, movie]: wyszukuje komórkę na przecięciu wiersza 'user' i kolumny 'movie'
        # - pd.isna(): zwraca True jeśli wartość to NaN (brak oceny) lub False jeśli ocena istnieje
        # - if not pd.isna(...): oznacza "jeśli ocena ISTNIEJE" -> rozkazujemy pomiń (continue)
        if not pd.isna(matrix.loc[user, movie]):
            continue

        # num (licznik): suma ważonych odchyleń ocen sąsiadów
        # den (mianownik): suma bezwzględnych wag podobieństwa sąsiadów
        num, den = 0.0, 0.0

        # pętla po wyselekcjonowanych k-sąsiadach:
        # - neighbors.items(): zwraca pary (imię_sąsiada, waga_podobieństwa)
        # - other: zmienna przechowująca imię sąsiada (np. "Celina")
        # - w: zmienna przechowująca wagę podobieństwa (np. 0.85)
        for other, w in neighbors.items():
            # pobranie oceny jaką ten sąsiad wystawił danemu filmowi (z użyciem .loc[wiersz, kolumna])
            r = matrix.loc[other, movie]

            # uwzględniamy tylko sąsiadów, którzy faktycznie widzieli i ocenili ten film (ocena nie jest NaN)
            if not pd.isna(r):
                # (r - means[other]): odchylenie oceny sąsiada od jego własnej średniej
                # w * (...): przemnożenie odchylenia przez wagę podobieństwa sąsiada do głównego usera
                num += w * (r - means[other])
                # abs(w): wartość bezwzględna z wagi podobieństwa (zapobiega ujemnym mianownikom)
                den += abs(w)

        # jeśli chociaż jeden sąsiad z k-najbliższych ocenił ten film (mianownik > 0)
        if den > 0:
            # wzór predykcji: osobista średnia usera + (ważona suma odchyleń sąsiadów / suma ich wag)
            predicted = means[user] + num / den

            # clamp (przycinanie): ograniczenie wyniku do dopuszczalnego zakresu ocen 1.0 - 5.0
            # - min(5.0, predicted): nie pozwala wartości przekroczyć 5.0
            # - max(1.0, ...): nie pozwala wartości spaść poniżej 1.0
            scores[movie] = max(1.0, min(5.0, predicted))

    # sortowanie wyliczonych ocen:
    # - scores.items(): zamienia słownik na listę par (tytuł, ocena)
    # - key=lambda x: x[1]: sortuje po drugim elemencie pary, czyli po ocenie
    # - reverse=True: sortowanie malejąco (od najwyższej oceny do najniższej)
    # - [:top_n]: wycięcie pierwszych top_n pozycji (domyślnie 5)
    best = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]

    # zwrócenie listy słowników w formacie gotowym do API:
    # - "title": t -> tytuł filmu
    # - "predicted": round(float(s), 2) -> zaokrąglenie oceny do 2 miejsc po przecinku
    # - "because": lista imion sąsiadów, którzy mieli niezerowe podobieństwo i ocenili ten konkretny film
    return [
        {
            "title": t,
            "predicted": round(float(s), 2),
            "because": [
                o
                for o, weight in neighbors.items()
                if weight != 0 and not pd.isna(matrix.loc[o, t])
            ],
        }
        for t, s in best
    ]


# test działania funkcji dla Ani
if __name__ == "__main__":
    print(recommend("Ania", top_n=3, k=3))

"""Ściągawka z org plików

Pipeline:
    ratings.csv  ->  pivot (użytkownicy x filmy)  ->  centrowanie na średnią usera
    ->  cosine między użytkownikami na wyśrodkowanych wektorach z zerami za braki
    ->  przewidywanie: średnia usera + średnia ważona odchyleń sąsiadów


Eliminacja stylu oceniania: Optymista daje ocenom zakres 4-5 (średnia 4.5), a krytyk 1-2 (średnia 1.5).
    Bez centrowania algorytm uzna, że się nie zgadzają, mimo że obaj uważają ten sam film za swój ulubiony.
Ominięcie "pułapki zer": Nieocenione filmy zastępujemy cyfrą 0.
    W wyśrodkowanej macierzy 0 oznacza brak odchylenia (dokładnie średnia usera), więc brak oceny nie zaburza wyników.


Dlaczego centrowanie? Porównujemy odchylenia od własnej średniej, a nie same
dodatnie oceny. Wspólne zera nie zwiększają iloczynu skalarnego. Licznik cosine
uwzględnia wspólnie ocenione filmy, ale normy całe wektory. Przy brakach nie
jest to Pearson liczony wyłącznie na przecięciu ocen; skale i małe przecięcie
nadal wymagają ostrożnej interpretacji.
"""