import threading
import time

from spotify import get_current_song
from genius import find_song, get_lyrics
from popup import create_popup, update_popup, start_popup


CHECK_INTERVAL = 3


# =========================
# BUSCAR LETRA
# =========================

def get_song_lyrics(song):

    title = song["title"]
    artists = song["artists"]

    # =========================
    # FORMATEAR ARTISTAS
    # =========================

    artist_list = [
        artist.strip()
        for artist in artists.split(",")
    ]

    if len(artist_list) > 1:

        display_artist = (
            artist_list[0]
            + " ft. "
            + ", ".join(artist_list[1:])
        )

    else:

        display_artist = artist_list[0]

    print("\n🎵 Canción actual")
    print("----------------------------")
    print(f"Artista: {display_artist}")
    print(f"Título:  {title}")

    # =========================
    # BUSCAR EN GENIUS
    # =========================

    genius_song = find_song(
        title,
        artists
    )

    if genius_song is None:

        return {
            "title": title,
            "artist": display_artist,
            "lyrics": (
                "No encontramos una coincidencia "
                "segura.\n\n"
                "💡 No mostramos ninguna letra "
                "porque no estamos seguros de que "
                "sea la canción correcta."
            )
        }

    # =========================
    # OBTENER LETRA
    # =========================

    lyrics = get_lyrics(
        genius_song
    )

    if lyrics is None:

        return {
            "title": genius_song["title"],
            "artist": display_artist,
            "lyrics": (
                "⚠️ Esta canción todavía "
                "no tiene letra.\n\n"
                "✍️ ¿Te animas a transcribirla "
                "y ayudar a otros usuarios?\n\n"
                f"{genius_song['url']}"
            )
        }

    return {
        "title": genius_song["title"],
        "artist": display_artist,
        "lyrics": lyrics
    }


# =========================
# MONITOR SPOTIFY
# =========================

def monitor_spotify():

    previous_song_id = None

    while True:

        try:

            song = get_current_song()

            # No hay canción
            if song is None:

                print(
                    "\n⏸️ No hay ninguna canción "
                    "reproduciéndose."
                )

                time.sleep(CHECK_INTERVAL)

                continue

            song_id = song["id"]

            # -------------------------
            # ¿HA CAMBIADO?
            # -------------------------

            if song_id != previous_song_id:

                print("\n🔄 Nueva canción detectada")

                previous_song_id = song_id

                result = get_song_lyrics(song)

                update_popup(
                    result["title"],
                    result["artist"],
                    result["lyrics"]
                )

            time.sleep(CHECK_INTERVAL)

        except Exception as error:

            print(
                f"\n❌ Error comprobando Spotify: "
                f"{error}"
            )

            time.sleep(CHECK_INTERVAL)


# =========================
# PRIMERA CANCIÓN
# =========================

song = get_current_song()

if song is None:

    print(
        "❌ No hay ninguna canción "
        "reproduciéndose."
    )

    exit()


result = get_song_lyrics(song)


# =========================
# CREAR POPUP
# =========================

create_popup(
    result["title"],
    result["artist"],
    result["lyrics"]
)


# =========================
# MONITOR EN SEGUNDO PLANO
# =========================

monitor_thread = threading.Thread(
    target=monitor_spotify,
    daemon=True
)

monitor_thread.start()


# =========================
# INICIAR POPUP
# =========================

start_popup()