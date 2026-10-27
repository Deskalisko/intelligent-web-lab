from unittest import result

import pandas as pd
from pyexpat import features
from sklearn.feature_extraction.text import TfidfVectorizer #słówka wypełniacze
from sklearn.metrics.pairwise import cosine_similarity # macierz prawdopodobienstwa
from scipy.sparse import hstack
from sklearn.preprocessing import MultiLabelBinarizer

# TF (Term Frequency): Im częściej słowo występuje w opisie jednego filmu, tym jest ważniejsze dla tego filmu.
# IDF (Inverse Document Frequency): Im rzadziej słowo występuje w całej bazie innych filmów, tym lepszym jest "wyróżnikiem".

df = pd.read_csv("movies.csv")
df["overview"] = df["overview"].fillna("") # wypełnienie brakow w opisach pustym tekstem
df["genres"] = df["genres"].fillna("") #brak gatunuku

# print(df.shape)           # (24, 4) - rozmiar tabeli / csv
# print(df.head(3))         # pierwsze wiersze
# print(df.isnull().sum())  # braki w kolumnach- nie ma

vectorizer = TfidfVectorizer(stop_words="english") #tworzy przelicznik tekstu na liczby z odrzuceniem angielskich slow wypelniaczy np: the, a, is, in.

#przekształca opisy ze wszystkich filmów na macierz liczbową tf-idf
tfidf_matrix = vectorizer.fit_transform(df["overview"])

#rozmiar macierzy (liczba filmów, liczba unikalnych słów)
# print(tfidf_matrix.shape) #24 filmy, 237 unikalnych

genres_list = [g.split("|") for g in df["genres"]] #zamiana tekstu Action|Sci-Fi na liste dwoch elementow tzn ['Action', 'Sci-Fi']
mlb = MultiLabelBinarizer()
genres_matrix = mlb.fit_transform(genres_list) #przekształcenie gatunków na wektory 0/1

features_matrix = hstack([tfidf_matrix, genres_matrix]) #polaczenie m,acierzy opisow z macierza gatunkow
sim_matrix = cosine_similarity(features_matrix) #macierze podobiestwa na podstawie wszystkich polaczonych cech


def recommend(title, top_n=5, genre=None):#funkcja zwraca 5 najbardziej podobnych filmow do tytułowego
    match = df[df["title"].str.lower() == title.lower()] #szukanie filmu (nie zależnie od wielkości liter)
    if match.empty:
        return None

    idx = match.index[0] #id znalezionego matcha

    #scores = sorted(enumerate(sim_matrix[idx]), key=lambda x: x[1], reverse=True)
    podobienstwa = sim_matrix[idx] #lista podobieństw dla naszego filmu

    pary_podobienstw = []
    for numer_filmu, wynik in enumerate(podobienstwa):
        pary_podobienstw.append((numer_filmu, wynik)) #tworzenie par (indeks filmu, wynik podobienstwa)

    scores = sorted(pary_podobienstw, key=lambda x: x[1], reverse=True) #posortowane pary od największego wyniku (sortowanie wedlug x1 -wyniku podobienstwa, x0 to indeks filmu)

    results = []
    for i, s in scores:
        if i == idx:
            continue  # pomijamy ten sam film

        movie_genres = df["genres"][i]

        #jesli podalismy filtr genre, pomijamy filmy niepasujące do gatunku
        if genre and genre.lower() not in movie_genres.lower():
            continue

        results.append({
            "title": df["title"][i],
            "genres": movie_genres,
            "rating": round(float(df["rating"][i]), 1),
            "score": round(float(s), 3)
        })

        #przerywanie gdyb mamy juz top_n
        if len(results) == top_n:
            break

    return results