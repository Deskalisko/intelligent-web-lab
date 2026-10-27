import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer #słówka wypełniacze
from sklearn.metrics.pairwise import cosine_similarity # macierz prawdopodobienstwa

# TF (Term Frequency): Im częściej słowo występuje w opisie jednego filmu, tym jest ważniejsze dla tego filmu.
# IDF (Inverse Document Frequency): Im rzadziej słowo występuje w całej bazie innych filmów, tym lepszym jest "wyróżnikiem".

df = pd.read_csv("movies.csv")
df["overview"] = df["overview"].fillna("") # wypełnienie brakow w opisach pustym tekstem

# print(df.shape)           # (24, 4) - rozmiar tabeli / csv
# print(df.head(3))         # pierwsze wiersze
# print(df.isnull().sum())  # braki w kolumnach- nie ma

vectorizer = TfidfVectorizer(stop_words="english") #tworzy przelicznik tekstu na liczby z odrzuceniem angielskich slow wypelniaczy np: the, a, is, in.

#przekształca opisy ze wszystkich filmów na macierz liczbową tf-idf
tfidf_matrix = vectorizer.fit_transform(df["overview"])

#rozmiar macierzy (liczba filmów, liczba unikalnych słów)
# print(tfidf_matrix.shape) #24 filmy, 237 unikalnych

sim_matrix = cosine_similarity(tfidf_matrix)   # 24 x 24, każdy z każdym - macierz prawdopodobienstwa


def recommend(title, top_n=5):#funkcja zwraca 5 najbardziej podobnych filmow do tytułowego
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

    return [
        {
            "title": df["title"][i],
            "genres": df["genres"][i],
            "rating": round(float(df["rating"][i]), 1),
            "score": round(float(s), 3) #wynik podobienstwa
        }
        for i, s in scores if i != idx
    ][:top_n]