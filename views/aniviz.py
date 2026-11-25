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


PAPER = "#F6F1E7"
INK = "#292723"
VERMILLION = "#B64735"
INDIGO = "#394266"
CHART_COLORS = [VERMILLION, INDIGO, "#A97936", "#647261", "#9A6E72"]
GRID = "#DED7CA"


def style_figure(figure):
    figure.update_layout(
        paper_bgcolor=PAPER,
        plot_bgcolor=PAPER,
        font={"family": "Georgia, serif", "color": INK},
        margin={"l": 12, "r": 12, "t": 28, "b": 12},
        legend={"font": {"color": INK}},
    )
    figure.update_xaxes(
        showgrid=True,
        gridcolor=GRID,
        zerolinecolor=GRID,
        linecolor=GRID,
        tickfont={"color": INK},
        title_font={"color": INK},
    )
    figure.update_yaxes(
        showgrid=True,
        gridcolor=GRID,
        zerolinecolor=GRID,
        linecolor=GRID,
        tickfont={"color": INK},
        title_font={"color": INK},
    )
    return figure


st.caption("02  ·  VISUALISATIONS")
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
chart_columns = st.columns(2, gap="large")
if not status_data.empty:
    with chart_columns[0]:
        st.subheader("Statuts de visionnage")
        status_figure = px.pie(
            status_data,
            names="Statut",
            values="Nombre d'animes",
            hole=0.5,
            color_discrete_sequence=CHART_COLORS,
        )
        status_figure.update_traces(
            marker_line_color=PAPER,
            marker_line_width=2,
            textfont={"color": INK},
            textinfo="none",
        )
        st.plotly_chart(style_figure(status_figure), width="stretch")

score_data = build_score_distribution(anime_df)
if int(score_data["Nombre d'animes"].sum()) == 0:
    with chart_columns[1]:
        st.subheader("Distribution des notes")
        st.info("Aucune note n'a encore été attribuée dans cette anime list.")
else:
    with chart_columns[1]:
        st.subheader("Distribution des notes")
        score_figure = px.bar(
            score_data,
            x="Note",
            y="Nombre d'animes",
            category_orders={"Note": list(range(1, 11))},
            color_discrete_sequence=[INDIGO],
        )
        score_figure.update_traces(marker_line_color=INDIGO)
        st.plotly_chart(style_figure(score_figure), width="stretch")

genre_data = build_genre_counts(anime_df).head(15)
if genre_data.empty:
    st.subheader("Genres les plus présents")
    st.info("Aucune information de genre n'est disponible.")
else:
    genre_column, activity_column = st.columns(2, gap="large")
    with genre_column:
        st.subheader("Genres les plus présents")
        genre_figure = px.bar(
            genre_data.sort_values("Nombre d'animes"),
            x="Nombre d'animes",
            y="Genre",
            orientation="h",
            color_discrete_sequence=[INDIGO],
        )
        genre_figure.update_traces(marker_line_color=INDIGO)
        genre_figure.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(style_figure(genre_figure), width="stretch")

activity_data = build_monthly_activity(anime_df)
if activity_data.empty:
    if genre_data.empty:
        activity_column = st.container()
    with activity_column:
        st.subheader("Activité récente")
        st.caption(
            "Nombre d'entrées modifiées par mois, d'après la dernière mise à "
            "jour MAL de chaque entrée (ce n'est pas un historique de visionnage)."
        )
        st.info("Aucune date de mise à jour exploitable n'est disponible.")
else:
    if genre_data.empty:
        activity_column = st.container()
    with activity_column:
        st.subheader("Activité récente")
        st.caption(
            "Nombre d'entrées modifiées par mois, d'après la dernière mise à "
            "jour MAL de chaque entrée (ce n'est pas un historique de visionnage)."
        )
        activity_figure = px.line(
            activity_data,
            x="Mois",
            y="Entrées modifiées",
            markers=True,
            color_discrete_sequence=[VERMILLION],
        )
        activity_figure.update_traces(
            line={"color": VERMILLION, "width": 3},
            marker={"color": INDIGO, "size": 8},
        )
        st.plotly_chart(style_figure(activity_figure), width="stretch")
