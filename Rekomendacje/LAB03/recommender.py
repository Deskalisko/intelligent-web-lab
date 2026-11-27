from difflib import get_close_matches
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd

df = pd.read_csv("ratings.csv")
matrix = df.pivot_table(index="user", columns="title", values="rating")

user_means = matrix.mean(axis=1)
centered_matrix = matrix.sub(user_means, axis=0).fillna(0)

sim_array = cosine_similarity(centered_matrix)
similarity_df = pd.DataFrame(
    sim_array, index=matrix.index, columns=matrix.index
)


def recommend(user, top_n=5, k=3):
    if user not in matrix.index:
        suggestions = get_close_matches(
            user, matrix.index.astype(str), n=3, cutoff=0.5
        )
        return {"suggestions": suggestions}

    neighbors = (
        similarity_df[user]
        .drop(user)
        .sort_values(ascending=False)
        .head(k)
    )

    predicted_scores = {}

    for movie in matrix.columns:
        if not pd.isna(matrix.loc[user, movie]):
            continue

        weighted_sum = 0.0
        weights_sum = 0.0

        for other_user, weight in neighbors.items():
            rating = matrix.loc[other_user, movie]

            if not pd.isna(rating):
                weighted_sum += weight * (rating - user_means[other_user])
                weights_sum += abs(weight)

        if weights_sum > 0:
            predicted_rating = user_means[user] + (weighted_sum / weights_sum)
            clamped_rating = max(1.0, min(5.0, predicted_rating))
            predicted_scores[movie] = clamped_rating
        else:
            global_movie_mean = matrix[movie].mean()
            if not pd.isna(global_movie_mean):
                predicted_scores[movie] = round(float(global_movie_mean), 2)

    best_movies = sorted(
        predicted_scores.items(), key=lambda item: item[1], reverse=True
    )[:top_n]

    results = [
        {
            "title": title,
            "predicted": round(float(score), 2),
            "because": [
                other
                for other, weight in neighbors.items()
                if weight != 0 and not pd.isna(matrix.loc[other, title])
            ],
        }
        for title, score in best_movies
    ]

    return {"recommendations": results}