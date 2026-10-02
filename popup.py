import webview


window = None


def load_html(title, artist, lyrics):

    with open(
        "ui/popup.html",
        "r",
        encoding="utf-8"
    ) as file:

        html = file.read()

    html = html.replace(
        "{{TITLE}}",
        title
    )

    html = html.replace(
        "{{ARTIST}}",
        artist
    )

    html = html.replace(
        "{{LYRICS}}",
        lyrics
    )

    return html


def create_popup(title, artist, lyrics):

    global window

    html = load_html(
        title,
        artist,
        lyrics
    )

    window = webview.create_window(
        "Lyrics Popup",
        html=html,
        width=450,
        height=650,
        resizable=True
    )

    return window


def update_popup(title, artist, lyrics):

    global window

    if window is None:
        return

    html = load_html(
        title,
        artist,
        lyrics
    )

    window.load_html(html)


def start_popup():

    webview.start()