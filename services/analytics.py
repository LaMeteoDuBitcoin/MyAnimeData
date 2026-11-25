from collections import Counter
from typing import Any

import pandas as pd


STATUS_LABELS = {
    "watching": "En cours",
    "completed": "Terminés",
    "on_hold": "En pause",
    "dropped": "Abandonnés",
    "plan_to_watch": "À voir",
}

ANIME_COLUMNS = [
    "title",
    "status",
    "score",
    "episodes_watched",
    "updated_at",
    "genres",
]


def build_anime_dataframe(entries: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for entry in entries:
        node = entry.get("node") or {}
        list_status = entry.get("list_status") or {}
        if not isinstance(node, dict) or not isinstance(list_status, dict):
            continue

        rows.append(
            {
                "title": node.get("title") or "Sans titre",
                "status": list_status.get("status"),
                "score": list_status.get("score"),
                "episodes_watched": list_status.get("num_episodes_watched") or 0,
                "updated_at": list_status.get("updated_at"),
                "genres": [
                    genre["name"]
                    for genre in (node.get("genres") or [])
                    if isinstance(genre, dict) and isinstance(genre.get("name"), str)
                ],
            }
        )
    return pd.DataFrame(rows, columns=ANIME_COLUMNS)


def summarize_anime_list(anime_df: pd.DataFrame) -> dict[str, Any]:
    scores = pd.to_numeric(anime_df["score"], errors="coerce")
    rated_scores = scores[scores.between(1, 10)]
    statuses = anime_df["status"].value_counts()
    completed = int(statuses.get("completed", 0))
    total = len(anime_df)

    return {
        "total_anime": total,
        "completed": completed,
        "episodes_watched": int(
            pd.to_numeric(anime_df["episodes_watched"], errors="coerce")
            .fillna(0)
            .sum()
        ),
        "average_score": float(rated_scores.mean()) if not rated_scores.empty else None,
        "rated_count": int(rated_scores.count()),
        "completion_percentage": (completed / total * 100) if total else 0.0,
        "status_counts": {
            STATUS_LABELS[status]: int(statuses.get(status, 0))
            for status in STATUS_LABELS
        },
    }


def build_score_distribution(anime_df: pd.DataFrame) -> pd.DataFrame:
    scores = pd.to_numeric(anime_df["score"], errors="coerce")
    scores = scores[scores.between(1, 10)].astype(int)
    counts = scores.value_counts().reindex(range(1, 11), fill_value=0)
    return counts.rename_axis("Note").reset_index(name="Nombre d'animes")


def build_genre_counts(anime_df: pd.DataFrame) -> pd.DataFrame:
    genres = Counter(
        genre
        for anime_genres in anime_df["genres"]
        for genre in set(anime_genres)
    )
    return pd.DataFrame(
        sorted(genres.items(), key=lambda item: (-item[1], item[0])),
        columns=["Genre", "Nombre d'animes"],
    )


def build_monthly_activity(anime_df: pd.DataFrame) -> pd.DataFrame:
    updated_at = pd.to_datetime(anime_df["updated_at"], errors="coerce", utc=True)
    months = updated_at.dt.tz_convert(None).dt.strftime("%Y-%m")
    counts = months.dropna().value_counts().sort_index()
    return counts.rename_axis("Mois").reset_index(name="Entrées modifiées")
