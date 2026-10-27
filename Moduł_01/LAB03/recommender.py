import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

df = pd.read_csv("ratings.csv") # kolumny w pliku to user, title, rating

matrix = df.pivot_table(index="user", columns="title", values="rating") # przekształcenie tabeli na macierz: wiersze to uzytkownicy itd.
#pivot tworzy wektory gustu (wiersze ) w jednej operacji zamiast (powolnej) petli
#macierz pozwala jednym działaniem zmierzyć podobienstwo całych profili


#wymiary: 12 wierszy (osoby) x 24 kolumny (filmy), NaN = nieoceniony
print(matrix.shape)  # (12, 24)



"""Ściągawka

Pipeline:
    ratings.csv  ->  pivot (użytkownicy x filmy)  ->  centrowanie na średnią usera
    ->  cosine między użytkownikami na wyśrodkowanych wektorach z zerami za braki
    ->  przewidywanie: średnia usera + średnia ważona odchyleń sąsiadów

Dlaczego centrowanie? Porównujemy odchylenia od własnej średniej, a nie same
dodatnie oceny. Wspólne zera nie zwiększają iloczynu skalarnego. Licznik cosine
uwzględnia wspólnie ocenione filmy, ale normy całe wektory. Przy brakach nie
jest to Pearson liczony wyłącznie na przecięciu ocen; skale i małe przecięcie
nadal wymagają ostrożnej interpretacji.
"""