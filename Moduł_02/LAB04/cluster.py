"""Lab 4: polskie artykuły -> TF-IDF -> K-Means. Uruchom: python cluster.py."""
import csv
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt # do wykresow

DATA = Path(__file__).with_name("articles.csv")
STOP = ["i", "w", "na", "do", "z", "o", "po", "dla", "oraz", "nad", "przed", "że", "się", "jest", "ma", "są"]


def load_articles():
    with DATA.open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def fit_articles(k=6, max_features=300, min_df=2):
    articles = load_articles()
    vectorizer = TfidfVectorizer(#tworzenie obiektu TF-IDF
        stop_words=STOP, #Usuwa mało znaczące słowa
        max_features=max_features, #wybiera max n np.100- tak jest wpisane w tym momencie- najważniejszych słów z całego zbioru, czyli z kilku tysięcy różnych słów zostaje 100 najistotniejszych
        min_df=min_df #teraz 2, czyli słowo musi wystąpić przynajmniej w 2 dokumentach
    )
    matrix = vectorizer.fit_transform( #(było to już w poprzednim labie) fit analizuje wszystkie artykuły i buduje słownik słów, natomiast transform zamienia tekst na liczby
        [f"{a['title']} {a['text']}" for a in articles]
    )
    model = KMeans(n_clusters=k, n_init=20, random_state=42).fit(matrix) #5 klastrów bo n_clusters=k, k = 5, n_init=20 tzn ze algorytm uruchamia się 20 razy i wybiera najlepszy wynik. ZIARNO czyli random_state=42 co sprawia ze wynik będzie powtarzalny
    return articles, vectorizer, matrix, model


def clusters(articles, vectorizer, model):
    words = vectorizer.get_feature_names_out() #pobiera wszystkie słowa użyte jako cechy
    result = []
    for cluster_id in range(model.n_clusters): # przechodzi po n clustrach u nas 5
        keywords = [words[i] for i in model.cluster_centers_[cluster_id].argsort()[-6:][::-1]] # dla centroidu pobiera jego wspolrzedne i sortuje wagi slow, wybiera 6 najwiekszych (::-1 -odwraca kolejnosc) od najwazniejszych
        docs = [dict(id=int(a["id"]), title=a["title"], text=a["text"])
                for a, label in zip(articles, model.labels_) if label == cluster_id]
        result.append(dict(cluster_id=cluster_id, keywords=keywords, articles=docs, count=len(docs)))
    return result


def elbow(matrix):
    return [{"k": k, "inertia": round(float(KMeans(n_clusters=k, n_init=10, random_state=42).fit(matrix).inertia_), 3)}
            for k in range(2, 9)]


if __name__ == "__main__":
    articles, vectorizer, matrix, model = fit_articles()
    print(f"{matrix.shape[0]} artykułów, {matrix.shape[1]} cech") # matrix shape pokazuje rozmiar macierzy tutaj został rozdzielony bo domyślnie wyswietliło by się (40, 100)
    for group in clusters(articles, vectorizer, model):
        print(group["cluster_id"], group["count"], ", ".join(group["keywords"][:4]))
    print("Elbow:", elbow(matrix))

    # wykresy

    # test dla różnych wartości k
    print("\nTEST RÓŻNYCH k\n")

    for k in range(2, 9):
        articles, vectorizer, matrix, model = fit_articles(
            k=k,
            max_features=300,
            min_df=2
        )

        print(f"\n===== k={k} =====")

        for group in clusters(articles, vectorizer, model):
            print(
                group["cluster_id"],
                group["count"],
                ", ".join(group["keywords"][:4])
            )

    # wykres łokcia
    articles, vectorizer, matrix, model = fit_articles(
        k=6,
        max_features=300,
        min_df=2
    )

    elbow_data = elbow(matrix)

    k_values = [item["k"] for item in elbow_data]
    inertia_values = [item["inertia"] for item in elbow_data]

    plt.figure(figsize=(8, 5))
    plt.plot(k_values, inertia_values, marker="o")
    plt.xlabel("Liczba klastrów (k)")
    plt.ylabel("Inercja")
    plt.title("Wykres 'łokcia'")
    plt.grid(True)
    plt.show()
