import streamlit as st

from services.analytics import build_anime_dataframe, summarize_anime_list
from services.mal_api import (
    MALAPIError,
    get_mal_client_id,
    get_user_anime_list,
)


st.title("Mon profil AniViz")
st.markdown(
    "Saisissez un nom d'utilisateur MyAnimeList dont l'anime list est publique."
)

saved_username = st.session_state.get("mal_username", "")
with st.form("mal_username_form"):
    username_input = st.text_input(
        "Nom d'utilisateur MyAnimeList",
        value=saved_username,
        placeholder="ex. votre_nom",
    )
    submitted = st.form_submit_button("Analyser mon profil")

if submitted:
    username = username_input.strip()
    if not username:
        st.error("Le nom d'utilisateur MyAnimeList est obligatoire.")
    else:
        st.session_state["mal_username"] = username

username = st.session_state.get("mal_username")
if not username:
    st.info("Entrez un nom d'utilisateur ci-dessus pour charger son anime list.")
    st.stop()

if st.button("Actualiser les données MAL", help="Ignore le cache et recharge la liste."):
    get_user_anime_list.clear()

try:
    client_id = get_mal_client_id()
    with st.spinner("Chargement de l'anime list depuis MyAnimeList..."):
        entries = get_user_anime_list(username, client_id)
except MALAPIError as exc:
    st.error(str(exc))
    st.stop()

anime_df = build_anime_dataframe(entries)
summary = summarize_anime_list(anime_df)
st.subheader(f"Anime list de {username}")
st.caption("Les données sont mises en cache pendant une heure.")

metrics = st.columns(4)
metrics[0].metric("Anime dans la liste", summary["total_anime"])
metrics[1].metric(
    "Terminés",
    summary["completed"],
    f"{summary['completion_percentage']:.1f} % de la liste",
)
metrics[2].metric("Épisodes vus", f"{summary['episodes_watched']:,}".replace(",", " "))
average_score = summary["average_score"]
metrics[3].metric(
    "Note moyenne",
    f"{average_score:.2f} / 10" if average_score is not None else "Non notée",
    f"{summary['rated_count']} anime notés",
)

st.subheader("Répartition par statut")
status_counts = summary["status_counts"]
status_columns = st.columns(len(status_counts))
for column, (status, count) in zip(status_columns, status_counts.items()):
    column.metric(status, count)

if not entries:
    st.info("Cette anime list ne contient pas encore d'entrée.")