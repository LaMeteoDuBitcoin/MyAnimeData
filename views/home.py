import streamlit as st

st.title("AniViz - Accueil")
st.markdown("""
Bienvenue sur AniViz, une application dédiée à l'analyse de votre anime list MyAnimeList.

Saisissez un nom d'utilisateur MAL dans la page **AniProfile** pour consulter vos indicateurs de progression, puis explorez les notes, les genres et l'activité de votre liste dans **AniViz**.
""")
st.markdown("""
## Données utilisées
Les données proviennent de l'API MyAnimeList. Les listes sont mises en cache pendant une heure afin de limiter les requêtes; l'actualisation peut être déclenchée depuis la page du profil. Le profil MAL doit être public.
""")