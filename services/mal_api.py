from typing import Any
from urllib.parse import quote, urlparse

import requests
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError


API_BASE_URL = "https://api.myanimelist.net/v2"
API_HOST = "api.myanimelist.net"
REQUEST_TIMEOUT_SECONDS = 15
PAGE_LIMIT = 1000


class MALAPIError(Exception):
    """Raised when MyAnimeList data cannot be retrieved or parsed."""


def get_mal_client_id() -> str:
    try:
        client_id = st.secrets["MAL_CLIENT_ID"]
    except (KeyError, StreamlitSecretNotFoundError) as exc:
        raise MALAPIError(
            "Le client ID MAL est manquant. Configurez MAL_CLIENT_ID "
            "dans .streamlit/secrets.toml."
        ) from exc

    if not isinstance(client_id, str) or not client_id.strip():
        raise MALAPIError("MAL_CLIENT_ID doit être une chaîne non vide.")
    return client_id.strip()


def _validate_api_url(url: str) -> None:
    parsed_url = urlparse(url)
    if parsed_url.scheme != "https" or parsed_url.netloc != API_HOST:
        raise MALAPIError("L'API MAL a retourné une URL de pagination invalide.")


def _request_json(
    url: str, client_id: str, params: dict[str, Any] | None = None
) -> dict[str, Any]:
    _validate_api_url(url)
    try:
        response = requests.get(
            url,
            headers={"X-MAL-CLIENT-ID": client_id},
            params=params,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise MALAPIError("Impossible de joindre l'API MyAnimeList.") from exc

    if response.status_code == 429:
        raise MALAPIError(
            "La limite de requêtes MyAnimeList est atteinte. Réessayez plus tard."
        )
    if response.status_code in (401, 403):
        raise MALAPIError(
            "MyAnimeList a refusé la requête. Vérifiez le client ID et "
            "la visibilité de la liste."
        )
    if response.status_code == 404:
        raise MALAPIError(
            "Profil ou anime list introuvable. Vérifiez le nom d'utilisateur "
            "et assurez-vous que sa liste est publique."
        )
    if response.status_code >= 400:
        detail = ""
        try:
            error_payload = response.json()
        except ValueError:
            error_payload = {}
        if isinstance(error_payload, dict):
            message = error_payload.get("message")
            if isinstance(message, str) and message.strip():
                if message.strip().casefold() == "invalid client id":
                    raise MALAPIError(
                        "MyAnimeList rejette MAL_CLIENT_ID. Vérifiez que vous avez "
                        "copié le « Client ID » depuis la configuration API MAL, "
                        "et non le « Client Secret », dans "
                        ".streamlit/secrets.toml."
                    )
                detail = f" Détail MAL : {message.strip()}"
        raise MALAPIError(
            f"L'API MyAnimeList a répondu avec le statut HTTP "
            f"{response.status_code}.{detail}"
        )
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        raise MALAPIError(
            f"L'API MyAnimeList a répondu avec le statut HTTP "
            f"{response.status_code}."
        ) from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise MALAPIError("La réponse de MyAnimeList n'est pas un JSON valide.") from exc

    if not isinstance(payload, dict):
        raise MALAPIError("La réponse de MyAnimeList a un format inattendu.")
    return payload


@st.cache_data(ttl=3600, show_spinner=False)
def get_user_anime_list(username: str, _client_id: str) -> list[dict[str, Any]]:
    """Fetch and cache every page of a user's anime list for one hour."""
    username = username.strip()
    if not username:
        raise MALAPIError("Le nom d'utilisateur MyAnimeList est obligatoire.")

    url = f"{API_BASE_URL}/users/{quote(username, safe='')}/animelist"
    params: dict[str, Any] | None = {
        "limit": PAGE_LIMIT,
        "fields": "list_status,genres",
    }
    results: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    while url:
        _validate_api_url(url)
        if url in seen_urls:
            raise MALAPIError("L'API MyAnimeList a retourné une pagination cyclique.")
        seen_urls.add(url)

        payload = _request_json(url, _client_id, params)
        page_data = payload.get("data")
        if not isinstance(page_data, list):
            raise MALAPIError("La réponse MyAnimeList ne contient pas une liste valide.")
        if any(not isinstance(item, dict) for item in page_data):
            raise MALAPIError("Une entrée de la réponse MyAnimeList a un format invalide.")
        results.extend(page_data)

        paging = payload.get("paging") or {}
        next_url = paging.get("next") if isinstance(paging, dict) else None
        if next_url is not None and not isinstance(next_url, str):
            raise MALAPIError("L'URL de pagination MyAnimeList est invalide.")
        url = next_url or ""
        params = None

    return results
