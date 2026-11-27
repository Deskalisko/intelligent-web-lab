"""py eksperyment.py: porównanie ustawień bez zmieniania CSV i kodu API."""
from math import isclose
from sklearn.metrics import adjusted_rand_score
from cluster import clusters, elbow, fit_articles

if __name__ == "__main__":
    for features, minimum in ((100, 2), (300, 2), (300, 1)): # testuje 3 warianty 100 cech, min_df=2; 300 cech, min_df=2; 300 cech, min_df=1
        articles, vectorizer, matrix, model = fit_articles( #trenowanie modelu, tworzy TF-IDF i uruchamia K'Means dla aktualnych parametrów
            max_features=features,
            min_df=minimum
        )
        groups = clusters(articles, vectorizer, model)
        assert matrix.shape[0] == len(articles) == 52#bylo 40 - trzeba bylo zmienic liczbe artykulow
        assert matrix.shape[1] <= features #to sprawdza czy liczba cech nie przekroczyła limitu (wymiarow macierzy) np.max 300 a nie zawsze 300
        assert sum(group["count"] for group in groups) == 52#bylo 40
        assert len({doc["id"] for group in groups for doc in group["articles"]}) == 52#bylo 40
        # Niezależnie odczytujemy odległość każdego punktu do jego centroida.
        distances = model.transform(matrix) # to liczby odleglosc kazdego artykulu do kazdego centroidu
        measured = sum( #reczne obliczanie inercji
            distances[i, label] ** 2
            for i, label in enumerate(model.labels_)
        )
        #weryfikacja inercji
        assert isclose(measured, model.inertia_, rel_tol=1e-9, abs_tol=1e-9)#czy recznie policzona zgadza sie z tą z Kmeans
        ari = adjusted_rand_score(
            [article["source"] for article in articles], #porownuje source czyli prawdziwe kategorie z
            model.labels_ #z labels, czyli klastrami podanymi przez kmeans
        )
        assert isclose(ari, adjusted_rand_score([article["source"] for article in articles], model.labels_ + 20))
        #wynik
        print(f"max_features={features}, min_df={minimum}, shape={matrix.shape}, ARI={ari:.3f}, inertia={model.inertia_:.3f}")
        if (features, minimum) == (100, 2):
            print("Elbow (ta sama macierz):", elbow(matrix))
