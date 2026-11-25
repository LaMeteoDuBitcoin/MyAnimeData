import unittest
from unittest.mock import Mock, call, patch

from services.mal_api import MALAPIError, get_user_anime_list


def make_response(payload, status_code=200):
    response = Mock()
    response.status_code = status_code
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    return response


class MALAPIClientTests(unittest.TestCase):
    def tearDown(self):
        get_user_anime_list.clear()

    @patch("services.mal_api.requests.get")
    def test_fetches_all_pages_and_uses_expected_fields(self, mock_get):
        mock_get.side_effect = [
            make_response(
                {
                    "data": [{"node": {"id": 1}}],
                    "paging": {
                        "next": "https://api.myanimelist.net/v2/users/test/animelist?offset=1000"
                    },
                }
            ),
            make_response({"data": [{"node": {"id": 2}}]}),
        ]

        entries = get_user_anime_list("test", "client-id")

        self.assertEqual([entry["node"]["id"] for entry in entries], [1, 2])
        self.assertEqual(mock_get.call_count, 2)
        self.assertEqual(
            mock_get.call_args_list[0],
            call(
                "https://api.myanimelist.net/v2/users/test/animelist",
                headers={"X-MAL-CLIENT-ID": "client-id"},
                params={
                    "limit": 1000,
                    "fields": "list_status,genres",
                },
                timeout=15,
            ),
        )
        self.assertIsNone(mock_get.call_args_list[1].kwargs["params"])

    @patch("services.mal_api.requests.get")
    def test_reuses_cached_list_for_same_username(self, mock_get):
        mock_get.return_value = make_response({"data": [{"node": {"id": 1}}]})

        first_result = get_user_anime_list("cached-user", "client-id")
        second_result = get_user_anime_list("cached-user", "client-id")

        self.assertEqual(first_result, second_result)
        self.assertEqual(mock_get.call_count, 1)

    @patch("services.mal_api.requests.get")
    def test_rejects_pagination_to_untrusted_host(self, mock_get):
        mock_get.return_value = make_response(
            {
                "data": [],
                "paging": {"next": "https://example.com/collect"},
            }
        )

        with self.assertRaisesRegex(MALAPIError, "URL de pagination invalide"):
            get_user_anime_list("test", "client-id")

        self.assertEqual(mock_get.call_count, 1)

    @patch("services.mal_api.requests.get")
    def test_reports_rate_limit(self, mock_get):
        mock_get.return_value = make_response({}, status_code=429)

        with self.assertRaisesRegex(MALAPIError, "limite de requêtes"):
            get_user_anime_list("test", "client-id")

        self.assertEqual(mock_get.call_count, 1)

    @patch("services.mal_api.requests.get")
    def test_includes_mal_error_detail_for_bad_request(self, mock_get):
        mock_get.return_value = make_response(
            {"error": "bad_request", "message": "Invalid fields"},
            status_code=400,
        )

        with self.assertRaisesRegex(MALAPIError, "Détail MAL : Invalid fields"):
            get_user_anime_list("test", "client-id")

        self.assertEqual(mock_get.call_count, 1)

    @patch("services.mal_api.requests.get")
    def test_explains_invalid_client_id(self, mock_get):
        mock_get.return_value = make_response(
            {"error": "bad_request", "message": "Invalid client id"},
            status_code=400,
        )

        with self.assertRaisesRegex(MALAPIError, "non le « Client Secret »"):
            get_user_anime_list("test", "client-id")

        self.assertEqual(mock_get.call_count, 1)


if __name__ == "__main__":
    unittest.main()
