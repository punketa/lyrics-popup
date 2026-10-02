import os
import re
import unicodedata

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv


load_dotenv()


GENIUS_API_URL = "https://api.genius.com/search"

API_HEADERS = {
    "Authorization": f"Bearer {os.getenv('GENIUS_ACCESS_TOKEN')}"
}

PAGE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/154.0.0.0 "
        "Safari/537.36"
    )
}


# =========================
# NORMALIZACIÓN
# =========================

def normalize(text):
    """
    Normaliza texto para poder comparar nombres
    independientemente de mayúsculas, tildes, espacios, etc.
    """

    text = text.lower()

    text = unicodedata.normalize("NFD", text)

    text = "".join(
        char
        for char in text
        if unicodedata.category(char) != "Mn"
    )

    text = re.sub(r"[^a-z0-9\s]", "", text)

    text = re.sub(r"\s+", " ", text).strip()

    return text


def normalize_compact(text):
    """
    Normaliza texto y elimina los espacios.
    """

    return normalize(text).replace(" ", "")


# =========================
# ARTISTAS
# =========================

def artist_words(text):

    normalized = normalize(text)

    return set(normalized.split())


def artists_match(spotify_artist, genius_artist):

    spotify_normalized = normalize_compact(
        spotify_artist
    )

    genius_normalized = normalize_compact(
        genius_artist
    )

    # Coincidencia exacta
    if spotify_normalized == genius_normalized:
        return "exact"

    spotify_words = artist_words(
        spotify_artist
    )

    genius_words = artist_words(
        genius_artist
    )

    # Ejemplo:
    # Tatox -> Tatox MDZ
    # Mixino -> Mixino Oficial
    if spotify_words and spotify_words.issubset(
        genius_words
    ):
        return "variant"

    if genius_words and genius_words.issubset(
        spotify_words
    ):
        return "variant"

    return None


# =========================
# BUSCAR CANCIÓN
# =========================

def find_song(title, artists):

    print("\n🔎 Buscando en Genius...")

    normalized_title = normalize_compact(title)

    spotify_artists = [
        artist.strip()
        for artist in artists.split(",")
    ]

    # -------------------------
    # CONSULTAS
    # -------------------------

    queries = []

    queries.append(title)

    for artist in spotify_artists:

        queries.append(
            f"{title} {artist}"
        )

    print("\nConsultas:")

    for query in queries:
        print(f"   🔎 {query}")

    # -------------------------
    # OBTENER RESULTADOS
    # -------------------------

    all_songs = {}

    for query in queries:

        params = {
            "q": query
        }

        response = requests.get(
            GENIUS_API_URL,
            headers=API_HEADERS,
            params=params,
            timeout=10
        )

        if response.status_code != 200:

            print(
                f"❌ Error buscando '{query}': "
                f"{response.status_code}"
            )

            continue

        data = response.json()

        hits = data["response"]["hits"]

        for hit in hits:

            song = hit["result"]

            all_songs[song["url"]] = song

    # -------------------------
    # COMPARAR RESULTADOS
    # -------------------------

    best_song = None
    best_score = 0

    for song in all_songs.values():

        genius_title = normalize_compact(
            song["title"]
        )

        genius_primary_artist = (
            song["primary_artist"]["name"]
        )

        score = 0

        # -------------------------
        # TÍTULO
        # -------------------------

        if genius_title == normalized_title:

            score += 50

        elif (
            normalized_title in genius_title
            or genius_title in normalized_title
        ):

            score += 20

        # -------------------------
        # ARTISTA PRINCIPAL
        # -------------------------

        for spotify_artist in spotify_artists:

            match = artists_match(
                spotify_artist,
                genius_primary_artist
            )

            if match == "exact":
                score += 100

            elif match == "variant":
                score += 80

        # -------------------------
        # FEATURED
        # -------------------------

        featured_artists = song.get(
            "featured_artists",
            []
        )

        for featured in featured_artists:

            genius_featured = featured["name"]

            for spotify_artist in spotify_artists:

                match = artists_match(
                    spotify_artist,
                    genius_featured
                )

                if match == "exact":
                    score += 80

                elif match == "variant":
                    score += 60

        print(
            f"   → {song['title']} - "
            f"{genius_primary_artist} "
            f"(score: {score})"
        )

        # -------------------------
        # GUARDAR MEJOR
        # -------------------------

        if score > best_score:

            best_score = score
            best_song = song

    # -------------------------
    # COMPROBAR MATCH
    # -------------------------

    if best_song is None or best_score < 100:

        print(
            "\n❌ No se encontró "
            "una coincidencia segura."
        )

        if best_song:

            print(
                f"Mejor resultado: "
                f"{best_song['title']} - "
                f"{best_song['primary_artist']['name']}"
            )

            print(
                f"Score: {best_score}"
            )

        print(
            "\n💡 No mostraremos ninguna letra "
            "porque no estamos seguros de que "
            "sea la canción correcta."
        )

        return None

    # -------------------------
    # MATCH ENCONTRADO
    # -------------------------

    print("\n✓ Canción encontrada")
    print("----------------------------")

    print(
        f"Título:  {best_song['title']}"
    )

    print(
        f"Artista: "
        f"{best_song['primary_artist']['name']}"
    )

    print(
        f"Score:   {best_score}"
    )

    print(
        f"URL:     {best_song['url']}"
    )

    return best_song


# =========================
# OBTENER LETRA
# =========================

def get_lyrics(song):

    print("\n📖 Comprobando letra...")

    response = requests.get(
        song["url"],
        headers=PAGE_HEADERS,
        timeout=10
    )

    if response.status_code != 200:

        print(
            f"⚠️ No se pudo acceder a la página "
            f"de Genius ({response.status_code})"
        )

        return None

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    lyrics_containers = soup.select(
        '[data-lyrics-container="true"]'
    )

    # -------------------------
    # NO HAY LETRA
    # -------------------------

    if not lyrics_containers:

        print(
            "\n⚠️ Esta canción todavía "
            "no tiene letra."
        )

        print(
            "✍️ ¿Te animas a transcribirla "
            "y ayudar a otros usuarios?"
        )

        print(
            f"\n👉 {song['url']}"
        )

        return None

    # -------------------------
    # HAY LETRA
    # -------------------------

    lyrics_parts = []

    for container in lyrics_containers:

        lyrics_parts.append(
            container.get_text(
                "\n",
                strip=True
            )
        )

    lyrics = "\n\n".join(
        lyrics_parts
    )

    print("\n✓ Letra encontrada")
    print("============================")

    return lyrics