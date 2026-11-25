from pathlib import Path

import streamlit as st

##########################
# ----- Page setup ----- #
##########################

st.set_page_config(
    page_title="AniViz",
    page_icon="📚",
    layout="wide",
)

logo_path = Path(__file__).resolve().parent / "design" / "aniviz-logo-proposal.svg"
st.sidebar.image(str(logo_path), width=220)

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
