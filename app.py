from flask import Flask, request, redirect, render_template, session
from spotufy import *
import os
import requests
import ast

# Inspiration for flask skeleton: 
# https://www.youtube.com/watch?v=dam0GPOAvVI
# https://www.youtube.com/watch?v=oVA0fD13NGI
# https://www.youtube.com/watch?v=MwZwr5Tvyxo
try:
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    secret_app_key = os.getenv("SECRET_KEY")
    flask_host = os.getenv("FLASK_HOST")
    flask_port = os.getenv("FLASK_PORT")
    callback_url = os.getenv("CALLBACK_URL")
except Exception as e:
    print(f"ERROR: {e}")
    print("Make sure the following environment variables are set:")
    print("CLIENT_ID\nCLIENT_SECRET\nSECRET_KEY\nFLASK_HOST\nFLASK_PORT\nCALLBACK_URL")

app = Flask(__name__)
app.secret_key = f"{secret_app_key}"


# Routes for the default pages such as home, search, etc.
@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html", token=session.get("access_token"))


@app.route("/search")
def search():
    return render_template("search.html", title="Song Details", token=session.get("access_token"))


@app.route("/tracks")
def tracks():
    return render_template("tracks.html", title="Search Tracks", token=session.get("access_token"))


@app.route("/track_details")
def search_tracks():
    return render_template("track_details.html", title="Song Details", token=session.get("access_token"))


@app.route("/recommendations")
def recommendations():
    return render_template("recommendations.html", title="Song Recommendations", token=session.get("access_token"))


@app.route("/related")
def related():
    return render_template("related.html", title="Related Artists", token=session.get("access_token"))


@app.route("/lyrics")
def lyrics():
    return render_template("lyrics.html", title="Get Lyrics", token=session.get("access_token"))


@app.route("/artist_releases")
def artist_releases():
    return render_template("artist_releases.html", title="Search Artist Releases", token=session.get("access_token"))


# Routes for the get functions when the user presses "Submit" on a form
@app.route("/get_search", methods=["POST", "GET"])
def search_artist():
    if request.method == "POST":
        name = request.form.get("search_artist")
        if name == "":
            return render_template("404.html", title="404 Not Found", token=session.get("access_token"))
        try:
            token = session.get("access_token")
            print(token)
            get_artists = search_artists(token, name)
            print(get_artists)
            return render_template("get_search.html", title="Search Artist", artists=get_artists, matched_artist=name,
                                   token=session.get("access_token"))
        except:
            return render_template("404.html", title="404 Not Found", token=session.get("access_token"))


@app.route("/get_top_tracks", methods=["POST", "GET"])
def get_tracks():
    if request.method == "POST":
        top_tracks = request.form.get("search_tracks")
        if top_tracks == "":
            return render_template("404.html", title="404 Not Found", token=session.get("access_token"))
        try:
            token = session.get("access_token")
            get_tracks_query = get_top_tracks(token, top_tracks)
        except:
            return render_template("404.html", title="404 Not Found", token=session.get("access_token"))
        return render_template("top_tracks.html", title="Search Tracks", tracks=get_tracks_query,
                               artist_title=top_tracks, token=session.get("access_token"))


@app.route("/get_track_details", methods=["POST", "GET"])
def get_track_details():
    if request.method == "POST":
        track_artist = request.form.get("search_details_artist")
        track_name = request.form.get("search_details_track")
        token = session.get("access_token")
        get_tracks_details = search_song_details(token, track_name, track_artist)
        print(get_tracks_details)
        if get_tracks_details is None:
            return render_template("404.html", title="404 Not Found", token=token)
        return render_template("get_track_details.html", title="Search Tracks", tracks=get_tracks_details,
                               artist=track_artist, name=track_name, token=session.get("access_token"))


@app.route("/get_recommendations", methods=["POST", "GET"])
def get_recommendations():
    if request.method == "POST":
        try:
            track_artist = request.form.get("recommendations_artist")
            track_name = request.form.get("recommendations_song")
            token = session.get("access_token")
            get_track_recommendations = get_track_recs(token, track_name, track_artist)
            # play_link = create_playlist(token, f"Recommended Songs based on {track_artist}", get_track_recommendations)
            return render_template("get_recommendations.html", title="Get Recommendations",
                                   tracks=get_track_recommendations, artist=track_artist, name=track_name,
                                   token=session.get("access_token"))
        except:
            return render_template("404.html", title="404 Not Found", token=session.get("access_token"))


@app.route("/get_related", methods=["POST", "GET"])
def search_related():
    if request.method == "POST":
        name = request.form.get("search_related")
        print(name)
        if name == "":
            return render_template("404.html", title="404 Not Found", token=session.get("access_token"))
        try:
            token = session.get("access_token")
            get_artists = search_artists(token, name)
            get_related_artist = get_related_artists(token, get_artists[1]["id"])
            print(get_related_artist)
            return render_template("get_related.html", title="Related Artists", related_artists=get_related_artist,
                                   matched_artist=name, token=session.get("access_token"))
        except:
            return render_template("404.html", title="404 Not Found", token=session.get("access_token"))


@app.route("/create_playlist", methods=["POST"])
def create_playlist_post():
    get_playlist_name = request.form['playlist_name']
    playlist_name = f"Recommended Songs based on {get_playlist_name.title()}"
    tracks_query = ast.literal_eval(request.form['tracks'])
    token = session.get("access_token")

    link = create_playlist(token, playlist_name, tracks_query)
    return redirect(link)


@app.route("/my_recommendations", methods=["GET"])
def my_recommendations():
    try:
        token = session.get("access_token")
        my_recs = get_user_recs(token)
        return render_template("my_recommendations.html", title="My Recommendations", recs=my_recs, token=token)
    except:
        return render_template("404.html", token=session.get("access_token"))


@app.route("/get_lyrics", methods=["GET", "POST"])
def get_lyrics():
    if request.method == "POST":
        artist_name = request.form.get("search_lyric_artist")
        artist_song = request.form.get("search_lyric_track")
        get_lyrics_query = get_genius_lyrics(artist_name, artist_song)
        return render_template("get_lyrics.html", title="Lyrics", token=session.get("access_token"),
                               lyrics=get_lyrics_query, name=artist_song, artist=artist_name)
    else:
        return render_template("404.html", title="404 Not Found", token=session.get("access_token"))


@app.route("/get_artist_releases", methods=["GET", "POST"])
def get_artist_release():
    if request.method == "POST":
        token = session.get("access_token")
        name = request.form.get("search_artist_releases")
        get_artists = search_artists(token, name)
        get_discography = get_artist_releases(token, get_artists[1])
        return render_template("get_discography.html", title="Artist Discography", token=session.get("access_token"),
                               name=name, discography=get_discography)


@app.route("/get_new_releases")
def get_new_release():
    new_releases = get_new_album_releases(session.get("access_token"))
    print(new_releases)
    return render_template("/new_albums.html", token=session.get("access_token"), album=new_releases)


@app.route("/login", methods=["POST","GET"])
def get_login_key():
    get_api_token = request_api_token()
    return get_api_token


@app.route("/logout", methods=["POST", "GET"])
def logout():
    session["access_token"] = None
    return render_template("index.html", token=None)


# Callback function credits: https://www.youtube.com/watch?v=olY_2MW4Eik
@app.route("/callback", methods=["GET"])
def callback():
    if "code" in request.args:
        req_body = {
            "code": request.args["code"],
            "grant_type": "authorization_code",
            "redirect_uri": callback_url,
            "client_id": client_id,
            "client_secret": client_secret
        }
        TOKEN_URL = "https://accounts.spotify.com/api/token"
        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()
        session["access_token"] = token_info["access_token"]
        return redirect("/")
    else:
        return render_template("404.html")


if __name__ == '__main__':
    app.run(host=flask_host, debug=True, port=flask_port)