import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv


load_dotenv()


def get_current_song():

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
            scope="user-read-currently-playing"
        )
    )

    current = sp.current_user_playing_track()

    if current is None or current["item"] is None:
        return None

    track = current["item"]

    title = track["name"]

    artists = ", ".join(
        artist["name"]
        for artist in track["artists"]
    )

    return {
        "id": track["id"],
        "title": title,
        "artists": artists
    }