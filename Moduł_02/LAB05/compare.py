"""Lab 5: porównanie K-Means, DBSCAN i Agglomerative na tych samych wektorach."""
from pathlib import Path
import sys
from time import perf_counter

from sklearn.cluster import AgglomerativeClustering, DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_distances

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from LAB04.cluster import fit_articles  # noqa: E402
#artykuly| tf-idf | artykuly na liczby | kmeans wytrenowy
articles, vectorizer, matrix, kmeans = fit_articles()
EPS = 0.74 #parametr dbscan - okresla max odleglosc miedzy punktami, by uznac ich za sasiadow, im wiekszy
#tym latwiej utworzyc grupe, jest mniej szuku i wieksze klastry
MIN_SAMPLES = 3 #min liczba punktow potrzebna do utworzenia rdzenia
dbscan = DBSCAN(eps=EPS, min_samples=MIN_SAMPLES, metric="cosine").fit(matrix)
agglomerative = AgglomerativeClustering(n_clusters=5, metric="cosine", linkage="average").fit(matrix.toarray())#klasteryzacja hierarchiczna
#zaczyna od pojedynczych punktow, stopniowo laczy najbardziej podobne grupy i konczy gdy zostanie (5) klastrow


def summary(name, labels, elapsed=None):
    kept = labels != -1
    groups = set(labels[kept])
    score = None
    if 1 < len(groups) < sum(kept):
        score = round(float(silhouette_score(matrix[kept], labels[kept], metric="cosine")), 3)
    return {"algorithm": name, "clusters": len(groups), "noise": int((~kept).sum()),
            "scored_articles": int(kept.sum()), "silhouette_cosine": score,
            "elapsed_ms": round(elapsed * 1000, 1) if elapsed is not None else None}


def compare():
    # Celowo mierzony jest sam fit, nie odczyt CSV ani TF-IDF.
    from sklearn.cluster import KMeans
    results = []
    for name, model, data in (
        ("K-Means", KMeans(n_clusters=5, n_init=20, random_state=42), matrix),
        ("DBSCAN", DBSCAN(eps=EPS, min_samples=MIN_SAMPLES, metric="cosine"), matrix),
        ("Agglomerative", AgglomerativeClustering(n_clusters=5, metric="cosine", linkage="average"), matrix.toarray()),
    ):
        start = perf_counter()
        labels = model.fit_predict(data)
        results.append(summary(name, labels, perf_counter() - start))
    return results


def assign_near_core(text):
    """Przypisanie do najbliższego punktu rdzeniowego; DBSCAN nie ma predict()."""
    sample = vectorizer.transform([text])
    if sample.nnz == 0 or len(dbscan.core_sample_indices_) == 0:
        return {"cluster_id": -1, "noise": True, "distance_to_core": None,
                "rule": "nearest_core_within_eps",
                "reason": "out_of_vocabulary" if sample.nnz == 0 else "no_core_points"}
    distances = cosine_distances(sample, dbscan.components_)[0]
    nearest = int(distances.argmin())
    distance = float(distances[nearest])
    cluster_id = int(dbscan.labels_[dbscan.core_sample_indices_[nearest]]) if distance <= EPS else -1
    return {"cluster_id": cluster_id, "noise": cluster_id == -1,
            "distance_to_core": round(distance, 3), "rule": "nearest_core_within_eps"}


if __name__ == "__main__":
    for row in compare():
        print(row)
    print("Artykuły oznaczone jako szum:")
    for article, label in zip(articles, dbscan.labels_):
        if label == -1:
            print(article["title"])
    print(assign_near_core("Nowa technologia urządzenia i aplikacja dla użytkowników"))
    print(assign_near_core("Archiwalne mapy gwiazd na dalekiej planecie"))
