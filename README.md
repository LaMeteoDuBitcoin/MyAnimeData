# AniViz - MyAnimeData

AniViz analyse l'anime list publique d'un utilisateur MyAnimeList et affiche des indicateurs de progression ainsi que des visualisations de ses notes, genres et activité.

## Installation

Utilisez Python 3.10 ou plus récent, puis installez les dépendances :

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Configurez un client ID de l'API MyAnimeList dans `.streamlit/secrets.toml`. Le fichier modèle peut être copié ainsi :

```bash
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Remplacez ensuite la valeur d'exemple par le **Client ID** créé dans la configuration API de MyAnimeList. N'utilisez pas le **Client Secret** à la place du Client ID. Le fichier `secrets.toml` local est ignoré par Git.

## Lancement

```bash
streamlit run app.py
```

Saisissez un nom d'utilisateur MAL public dans **AniProfile**. Les données sont conservées en cache pendant une heure; le bouton d'actualisation du profil recharge explicitement l'anime list. Les graphiques de la page **AniViz** réutilisent le cache.

## Tests

Les tests utilisent des données fictives et des réponses HTTP simulées; ils ne contactent pas MyAnimeList.

```bash
python -m unittest discover -s tests
```
