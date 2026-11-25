from pathlib import Path

import streamlit as st

logo_path = Path(__file__).resolve().parents[1] / "design" / "aniviz-logo-proposal.svg"
st.image(str(logo_path), width=300)

st.caption("ANIVIZ  ·  CARNET DE VISIONNAGE")
st.title("Une autre lecture de votre anime list")
st.write(
    "AniViz transforme votre liste publique MyAnimeList en indicateurs de "
    "progression et en repères visuels, dans un esprit manga sobre."
)

intro, details = st.columns([1.5, 1], gap="large")
with intro:
    with st.container(border=True):
        st.subheader("Commencez par votre profil")
        st.write(
            "Saisissez un nom d'utilisateur MAL dans **AniProfile** pour "
            "consulter votre progression, puis explorez les notes, les genres "
            "et l'activité de votre liste dans **AniViz**."
        )
        st.info("Votre profil MyAnimeList doit être public.")

with details:
    with st.container(border=True):
        st.subheader("Données, simplement")
        st.write(
            "Les données proviennent de l'API MyAnimeList. Les listes sont "
            "mises en cache pendant une heure afin de limiter les requêtes."
        )
        st.caption(
            "L'actualisation peut être déclenchée depuis la page du profil."
        )

st.subheader("Dans votre carnet")
feature_columns = st.columns(3, gap="medium")
features = (
    ("Progression", "Volume de la liste, épisodes vus et séries terminées."),
    ("Notes & genres", "Répartition des notes et genres les plus présents."),
    ("Activité", "Dernières mises à jour mensuelles de votre liste."),
)
for column, (title, description) in zip(feature_columns, features):
    with column:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(description)
