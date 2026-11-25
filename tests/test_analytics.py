import unittest

from services.analytics import (
    build_anime_dataframe,
    build_genre_counts,
    build_monthly_activity,
    build_score_distribution,
    summarize_anime_list,
)


class AnimeAnalyticsTests(unittest.TestCase):
    def setUp(self):
        self.entries = [
            {
                "node": {
                    "title": "First Anime",
                    "genres": [{"name": "Action"}, {"name": "Drama"}],
                },
                "list_status": {
                    "status": "completed",
                    "score": 8,
                    "num_episodes_watched": 12,
                    "updated_at": "2025-01-15T12:00:00+00:00",
                },
            },
            {
                "node": {
                    "title": "Second Anime",
                    "genres": [{"name": "Action"}],
                },
                "list_status": {
                    "status": "watching",
                    "score": 10,
                    "num_episodes_watched": 3,
                    "updated_at": "2025-01-20T12:00:00+00:00",
                },
            },
            {
                "node": {"title": "Third Anime", "genres": []},
                "list_status": {
                    "status": "plan_to_watch",
                    "score": 0,
                    "num_episodes_watched": 0,
                    "updated_at": "2025-02-02T12:00:00+00:00",
                },
            },
        ]
        self.anime_df = build_anime_dataframe(self.entries)

    def test_summary_excludes_unscored_titles(self):
        summary = summarize_anime_list(self.anime_df)

        self.assertEqual(summary["total_anime"], 3)
        self.assertEqual(summary["completed"], 1)
        self.assertEqual(summary["episodes_watched"], 15)
        self.assertEqual(summary["average_score"], 9.0)
        self.assertEqual(summary["rated_count"], 2)
        self.assertAlmostEqual(summary["completion_percentage"], 100 / 3)
        self.assertEqual(summary["status_counts"]["À voir"], 1)

    def test_chart_data_counts_scores_genres_and_months(self):
        score_data = build_score_distribution(self.anime_df)
        genre_data = build_genre_counts(self.anime_df).set_index("Genre")
        activity_data = build_monthly_activity(self.anime_df).set_index("Mois")

        self.assertEqual(len(score_data), 10)
        self.assertEqual(score_data.loc[7, "Nombre d'animes"], 1)
        self.assertEqual(genre_data.loc["Action", "Nombre d'animes"], 2)
        self.assertEqual(activity_data.loc["2025-01", "Entrées modifiées"], 2)
        self.assertEqual(activity_data.loc["2025-02", "Entrées modifiées"], 1)

    def test_empty_list_returns_empty_chart_data(self):
        empty_df = build_anime_dataframe([])

        self.assertIsNone(summarize_anime_list(empty_df)["average_score"])
        self.assertTrue(build_genre_counts(empty_df).empty)
        self.assertTrue(build_monthly_activity(empty_df).empty)


if __name__ == "__main__":
    unittest.main()
