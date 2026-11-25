import streamlit as st
import plotly.express as px

from services.analytics import (
    STATUS_LABELS,
    build_anime_dataframe,
    build_genre_counts,
    build_monthly_activity,
    build_score_distribution,
)
from services.mal_api import (
    MALAPIError,
    get_mal_client_id,
    get_user_anime_list,
)


st.title("Visualisations de l'anime list")
username = st.session_state.get("mal_username")
if not username:
    st.info("Commencez par analyser un profil dans la page AniProfile.")
    st.stop()

try:
    client_id = get_mal_client_id()
    with st.spinner("Chargement des données en cache..."):
        entries = get_user_anime_list(username, client_id)
except MALAPIError as exc:
    st.error(str(exc))
    st.stop()

anime_df = build_anime_dataframe(entries)
if anime_df.empty:
    st.info("Cette anime list ne contient pas encore d'entrée à visualiser.")
    st.stop()

st.caption(f"Analyse de l'anime list de {username}.")

status_data = anime_df["status"].value_counts().rename_axis("Statut").reset_index(
    name="Nombre d'animes"
)
status_data["Statut"] = status_data["Statut"].map(STATUS_LABELS).fillna("Autre")
if not status_data.empty:
    st.subheader("Statuts de visionnage")
    st.plotly_chart(
        px.pie(status_data, names="Statut", values="Nombre d'animes", hole=0.45),
        width="stretch",
    )

st.subheader("Distribution des notes")
score_data = build_score_distribution(anime_df)
if int(score_data["Nombre d'animes"].sum()) == 0:
    st.info("Aucune note n'a encore été attribuée dans cette anime list.")
else:
    st.plotly_chart(
        px.bar(
            score_data,
            x="Note",
            y="Nombre d'animes",
            title="Nombre d'animes par note",
            category_orders={"Note": list(range(1, 11))},
        ),
        width="stretch",
    )

st.subheader("Genres les plus présents")
genre_data = build_genre_counts(anime_df).head(15)
if genre_data.empty:
    st.info("Aucune information de genre n'est disponible.")
else:
    st.plotly_chart(
        px.bar(
            genre_data.sort_values("Nombre d'animes"),
            x="Nombre d'animes",
            y="Genre",
            orientation="h",
            title="Nombre d'animes par genre",
        ),
        width="stretch",
    )

st.subheader("Activité récente")
st.caption(
    "Nombre d'entrées modifiées par mois, d'après la dernière mise à jour MAL "
    "de chaque entrée (ce n'est pas un historique de visionnage)."
)
activity_data = build_monthly_activity(anime_df)
if activity_data.empty:
    st.info("Aucune date de mise à jour exploitable n'est disponible.")
else:
    st.plotly_chart(
        px.line(
            activity_data,
            x="Mois",
            y="Entrées modifiées",
            markers=True,
            title="Entrées modifiées par mois",
        ),
        width="stretch",
    )