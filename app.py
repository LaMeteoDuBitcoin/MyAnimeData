import streamlit as st

##########################
# ----- Page setup ----- #
##########################

accueil_page = st.Page(
    page="views/home.py",
    title="Accueil",
    icon="🏠",
    default=True
)

AniProfile = st.Page(
    page="views/aniprofile.py",
    title="AniProfile",
    icon="👤"
)

AniViz = st.Page(
    page="views/aniviz.py",
    title="AniViz",
    icon="📊"
)



###########################
# ----- Navigation ------ #
###########################

pg = st.navigation(
    {
        "Accueil": [accueil_page],
        "Fenêtre": [AniProfile, AniViz]
    }
)

pg.run()