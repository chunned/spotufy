from flask import Flask,url_for,request,render_template,redirect,session
import main,api
import dotenv
import urllib
import requests
import webbrowser
import lyricsgenius

apiSecrets = dotenv.dotenv_values('.env')
client_id = apiSecrets["CLIENT_ID"]
client_secret = apiSecrets["CLIENT_SECRET"]
secret_app_key = apiSecrets["SECRET_KEY"]

app = Flask(__name__)
app.secret_key = f"{secret_app_key}"

#routes for the default pages, e.g. home, search page
@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html",token=session.get("access_token"))

@app.route("/search")
def search():
    return render_template("search.html",title="Song Details",token=session.get("access_token"))

@app.route("/tracks")
def tracks():
    return render_template("tracks.html",title="Search Tracks",token=session.get("access_token"))

@app.route("/track_details")
def search_tracks():
    return render_template("track_details.html",title="Song Details",token=session.get("access_token"))

@app.route("/recommendations")
def recommendations():
    return render_template("recommendations.html",title="Song Recommendations",token=session.get("access_token"))

@app.route("/related")
def related():
    return render_template("related.html",title="Related Artists",token=session.get("access_token"))

@app.route("/lyrics")
def lyrics():
    return render_template("lyrics.html",title="Get Lyrics",token=session.get("access_token"))

@app.route("/artist_releases")
def artist_releases():
    return render_template("artist_releases.html",title="Search Artist Releases",token=session.get("access_token"))

# routes for the get functions (when they press submit on form)
@app.route("/get_search",methods=["POST","GET"])
def search_artist():
    if request.method == "POST":
        name = request.form.get("search_artist")
        print(name)
        if name == "": 
            return render_template("404.html",title="404 Not Found",token=session.get("access_token"))
        try: 
            token = session.get("access_token")
            print(token)
            get_artists = main.searchArtists(token, name)
        except: 
            return render_template("404.html",title="404 Not Found",token=session.get("access_token"))
        return render_template("get_search.html",title="Search Artist",artists=get_artists,matched_artist=name,token=session.get("access_token"))

@app.route("/get_top_tracks",methods=["POST","GET"])
def get_tracks():
    if request.method == "POST":
        top_tracks = request.form.get("search_tracks")
        if top_tracks == "": 
            return render_template("404.html",title="404 Not Found",token=session.get("access_token"))
        try: 
            token = session.get("access_token")
            get_tracks = main.get_top_tracks(token, top_tracks)
        except: 
            return render_template("404.html",title="404 Not Found",token=session.get("access_token"))
        return render_template("top_tracks.html",title="Search Tracks",tracks=get_tracks,artist_title=top_tracks,token=session.get("access_token"))

@app.route("/get_track_details",methods=["POST","GET"])
def get_track_details():
    if request.method == "POST":
        track_artist = request.form.get("search_details_artist")
        track_name = request.form.get("search_details_track")
        token = session.get("access_token")
        get_tracks_details = main.searchSongDetails(token, track_name, track_artist)
        print(get_tracks_details)
        if get_tracks_details == None:
            return render_template("404.html",title="404 Not Found",token=token)
        return render_template("get_track_details.html", title="Search Tracks", tracks=get_tracks_details, artist=track_artist, name=track_name,token=session.get("access_token"))
@app.route("/get_recommendations",methods=["POST","GET"])
def get_recommendations():
    if request.method == "POST":
        try: 
            track_artist = request.form.get("recommendations_artist")
            track_name = request.form.get("recommendations_song")
            token = session.get("access_token")
            print(token)
            get_track_recommendations = main.getTrackRecs(token, track_name, track_artist)
            print(get_track_recommendations)
            play_link = main.create_playlist(token,f"Recommended Songs based on {track_artist}",get_track_recommendations)
            print(play_link)
            return render_template("get_recommendations.html", title="Get Recommendations", tracks=get_track_recommendations, artist=track_artist, name=track_name,playlist_link=play_link, 
                               token=session.get("access_token"))
        except:
            return render_template("404.html",title="404 Not Found",token=session.get("access_token"))
        
@app.route("/get_related",methods=["POST","GET"])
def search_related():
    if request.method == "POST":
        name = request.form.get("search_related")
        print(name)
        if name == "": 
            return render_template("404.html",title="404 Not Found",token=session.get("access_token"))
        try: 
            token = session.get("access_token")
            get_artists = main.searchArtists(token, name)
            get_related_artists = main.getRelatedArtists(token,get_artists[1]["id"])
            return render_template("get_related.html",title="Related Artists",related_artists=get_related_artists,matched_artist=name,token=session.get("access_token"))
        except: 
            return render_template("404.html",title="404 Not Found",token=token)

@app.route("/my_recommendations",methods=["GET"])
def my_recommendations():
    try: 
        token = session.get("access_token")
        my_recs = main.getUserRecs(token)
        print(my_recs)
        return render_template("my_recommendations.html",title="My Recommendations",recs=my_recs,token=token)
    except:
        return render_template("404.html",token=token)

@app.route("/get_lyrics",methods=["GET","POST"])
def get_lyrics():
    if  request.method == "POST":
        artist_name = request.form.get("search_lyric_artist")
        artist_song = request.form.get("search_lyric_track")
        get_lyrics = main.get_genius_lyrics(artist_name,artist_song)
        print(get_lyrics)   
    return render_template("get_lyrics.html",title="Lyrics",token=session.get("access_token"),lyrics=get_lyrics,name=artist_song,artist=artist_name)

@app.route("/get_artist_releases",methods=["GET","POST"])
def get_artist_releases():
    if request.method == "POST":
        token = session.get("access_token")
        name = request.form.get("search_artist_releases")
        get_artists = main.searchArtists(token,name)
        get_discography =  main.getArtistReleases(token,get_artists[1])
        print(get_discography)
        return render_template("get_discography.html",title="Artist Discography",token=session.get("access_token"),name=name,discography=get_discography)


@app.route("/login",methods=["POST","GET"])
def get_login_key():
    get_api_token = api.request_api_token()
    return get_api_token

@app.route("/logout",methods=["POST","GET"])
def logout():
    session["access_token"] = None
    return render_template("index.html",token=None)

# entire callback function credits : https://www.youtube.com/watch?v=olY_2MW4Eik
@app.route("/callback",methods=["GET"])
def callback():
    if "code" in request.args:
        req_body = {
            "code" : request.args["code"],
            "grant_type" : "authorization_code",
            "redirect_uri" : 'http://192.168.2.252:9191/callback',
            "client_id" : client_id,
            "client_secret" : client_secret
        }
        TOKEN_URL = "https://accounts.spotify.com/api/token"
        response = requests.post(TOKEN_URL,data=req_body)
        token_info = response.json()
        print(token_info["access_token"])
        session["access_token"] = token_info["access_token"]
        return redirect("/")
    else:
        return render_template("404.html")

if __name__ == '__main__':
    app.run(host="192.168.2.252", debug=True, port=9191)
    
