"""
backend.py
=====================================================
Content-Based Tourist Destination Recommendation Engine
=====================================================
Algorithm : k-Nearest Neighbors (cosine similarity)
Features  : TF-IDF on tags + normalized numeric category scores
Filters   : province, budget, travel days, season (best_months)

Usage (from Streamlit or anywhere else):
    from backend import DestinationRecommender

    engine = DestinationRecommender("cleaned_travel_DATASET.csv")

    # Mode 1: "More like this" (item-based)
    results = engine.recommend_similar("Satasidham", top_k=5)

    # Mode 2: Preference-quiz based (user profile)
    results = engine.recommend_from_preferences(
        preferences={"culture": 5, "adventure": 2, "wildlife": 0,
                     "sightseeing": 4, "history": 3},
        top_k=5
    )

    # Both modes accept optional filters:
    results = engine.recommend_similar(
        "Satasidham", top_k=5,
        province=1, max_budget=20000, travel_days=2, month="October"
    )
"""

import ast
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import hstack, csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors

NUM_COLS = ["culture", "adventure", "wildlife", "sightseeing", "history"]
TAG_WEIGHT = 0.6
NUM_WEIGHT = 0.4


class DestinationRecommender:
    """
    Content-based recommender for tourist destinations.
    Wraps TF-IDF (tags) + Min-Max scaled numeric features into a single
    similarity space, searched via k-Nearest Neighbors with cosine distance.
    """

    def __init__(self, data_path: str, model_cache_path: str = "model_cache.pkl"):
        self.data_path = data_path
        self.model_cache_path = Path(model_cache_path)
        self._load_data()
        self._load_or_build_model()

    # ------------------------------------------------------------------
    # DATA LOADING
    # ------------------------------------------------------------------
    def _load_data(self):
        df = pd.read_csv(self.data_path)

        # tags_clean_list and best_months are stored as string-repr lists in CSV
        for col in ["tags_clean_list", "best_months"]:
            if col in df.columns and isinstance(df[col].iloc[0], str):
                df[col] = df[col].apply(
                    lambda x: ast.literal_eval(x) if isinstance(x, str) else x
                )

        df = df.reset_index(drop=True)
        self.df = df
        self.n_items = len(df)

    # ------------------------------------------------------------------
    # MODEL BUILDING (with caching so we don't retrain every app restart)
    # ------------------------------------------------------------------
    def _load_or_build_model(self):
        if self.model_cache_path.exists():
            try:
                with open(self.model_cache_path, "rb") as f:
                    cache = pickle.load(f)
                if cache.get("n_items") == self.n_items:
                    self.tfidf = cache["tfidf"]
                    self.scaler = cache["scaler"]
                    self.combined_matrix = cache["combined_matrix"]
                    self.knn_model = cache["knn_model"]
                    return
            except Exception:
                pass  # fall through and rebuild if cache is corrupt/stale

        self._build_model()
        self._save_cache()

    def _build_model(self):
        self.tfidf = TfidfVectorizer()
        tfidf_matrix = self.tfidf.fit_transform(self.df["tags_clean"])

        self.scaler = MinMaxScaler()
        numeric_scaled = self.scaler.fit_transform(self.df[NUM_COLS])
        numeric_matrix = csr_matrix(numeric_scaled)

        self.combined_matrix = hstack([
            tfidf_matrix.multiply(TAG_WEIGHT),
            numeric_matrix.multiply(NUM_WEIGHT)
        ]).tocsr()

        self.knn_model = NearestNeighbors(metric="cosine", algorithm="brute")
        self.knn_model.fit(self.combined_matrix)

    def _save_cache(self):
        with open(self.model_cache_path, "wb") as f:
            pickle.dump({
                "n_items": self.n_items,
                "tfidf": self.tfidf,
                "scaler": self.scaler,
                "combined_matrix": self.combined_matrix,
                "knn_model": self.knn_model,
            }, f)

    # ------------------------------------------------------------------
    # FILTERING (applied AFTER similarity ranking)
    # ------------------------------------------------------------------
    def _apply_filters(self, candidate_indices, province=None, max_budget=None,
                        min_budget=None, travel_days=None, month=None):
        df = self.df
        mask = pd.Series(True, index=df.index)

        if province is not None:
            mask &= (df["province"] == province)

        if max_budget is not None:
            mask &= (df["min_estimated_cost_per_person"] <= max_budget)

        if min_budget is not None:
            mask &= (df["max_estimated_cost_per_person"] >= min_budget)

        if travel_days is not None:
            mask &= (df["min_travel_days"] <= travel_days) & (df["max_travel_days"] >= travel_days)

        if month is not None:
            mask &= df["best_months"].apply(lambda months: month in months)

        allowed = set(df.index[mask])
        return [i for i in candidate_indices if i in allowed]

    # ------------------------------------------------------------------
    # MODE 1: ITEM-BASED "MORE LIKE THIS"
    # ------------------------------------------------------------------
    def recommend_similar(self, place_name: str, top_k: int = 5, **filters):
        matches = self.df.index[self.df["pName"] == place_name].tolist()
        if not matches:
            return {"error": f"Destination '{place_name}' not found."}

        idx = matches[0]
        query_vector = self.combined_matrix[idx]

        # over-fetch neighbors since filters may remove some candidates
        fetch_k = min(top_k * 5 + 10, self.n_items)
        distances, indices = self.knn_model.kneighbors(query_vector, n_neighbors=fetch_k)
        distances, indices = distances.flatten(), indices.flatten()

        candidates = [i for i in indices if i != idx]
        candidates = self._apply_filters(candidates, **filters)
        candidates = candidates[:top_k]

        return self._format_results(candidates, indices, distances)

    # ------------------------------------------------------------------
    # MODE 2: USER PREFERENCE PROFILE (quiz-based)
    # ------------------------------------------------------------------
    def recommend_from_preferences(self, preferences: dict, top_k: int = 5,
                                    preferred_tags: str = "", **filters):
        """
        preferences: dict with keys culture/adventure/wildlife/sightseeing/history (0-5 scale)
        preferred_tags: optional free-text string, e.g. "temple hiking lake"
        """
        num_values = pd.DataFrame([[preferences.get(c, 0) for c in NUM_COLS]], columns=NUM_COLS)
        num_scaled = self.scaler.transform(num_values)
        num_vec = csr_matrix(num_scaled)

        tag_vec = self.tfidf.transform([preferred_tags])

        query_vector = hstack([
            tag_vec.multiply(TAG_WEIGHT),
            num_vec.multiply(NUM_WEIGHT)
        ]).tocsr()

        fetch_k = min(top_k * 5 + 10, self.n_items)
        distances, indices = self.knn_model.kneighbors(query_vector, n_neighbors=fetch_k)
        distances, indices = distances.flatten(), indices.flatten()

        candidates = self._apply_filters(list(indices), **filters)[:top_k]

        return self._format_results(candidates, indices, distances)

    # ------------------------------------------------------------------
    # RESULT FORMATTING
    # ------------------------------------------------------------------
    def _format_results(self, candidates, all_indices, all_distances):
        dist_lookup = dict(zip(all_indices, all_distances))
        rows = []
        for i in candidates:
            row = self.df.iloc[i]
            similarity = 1 - dist_lookup.get(i, 1.0)
            rows.append({
                "pID": int(row["pID"]),
                "pName": row["pName"],
                "province": int(row["province"]),
                "culture": row["culture"], "adventure": row["adventure"],
                "wildlife": row["wildlife"], "sightseeing": row["sightseeing"],
                "history": row["history"],
                "tags": row["tags_clean"],
                "travel_days": f'{row["min_travel_days"]}-{row["max_travel_days"]}',
                "cost_per_person": f'{row["min_estimated_cost_per_person"]}-{row["max_estimated_cost_per_person"]}',
                "best_months": ", ".join(row["best_months"]),
                "similarity_score": round(float(similarity), 3),
            })
        return pd.DataFrame(rows)

    # ------------------------------------------------------------------
    # UTILITIES for the Streamlit frontend
    # ------------------------------------------------------------------
    def get_all_place_names(self):
        return sorted(self.df["pName"].unique().tolist())

    def get_provinces(self):
        return sorted(self.df["province"].unique().tolist())

    def get_place_details(self, place_name: str):
        matches = self.df[self.df["pName"] == place_name]
        if matches.empty:
            return None
        return matches.iloc[0].to_dict()


# ------------------------------------------------------------------
# QUICK SELF-TEST (only runs if this file is executed directly)
# ------------------------------------------------------------------
if __name__ == "__main__":
    engine = DestinationRecommender("cleaned_travel_DATASET.csv")

    print("=== Item-based recommendation ===")
    print(engine.recommend_similar("Satasidham", top_k=5))

    print("\n=== Item-based with filters (province=1, max_budget=20000) ===")
    print(engine.recommend_similar("Satasidham", top_k=5, province=1, max_budget=20000))

    print("\n=== Preference-based recommendation ===")
    prefs = {"culture": 5, "adventure": 1, "wildlife": 0, "sightseeing": 4, "history": 3}
    print(engine.recommend_from_preferences(prefs, top_k=5, preferred_tags="hindu temple"))