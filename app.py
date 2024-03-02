from flask import Flask,url_for,request,render_template
app = Flask(__name__)
import main

@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")

@app.route("/tracks")
def tracks():
    return render_template("tracks.html",title="Search Tracks")

@app.route("/track_details")
def search_tracks():
    return render_template("track_details.html",title="Song Details")

@app.route("/search")
def search():
    return render_template("search.html",title="Song Details")

@app.route("/get_search",methods=["POST","GET"])
def search_artist():
    if request.method == "POST":
        name = request.form.get("search_artist")
        print(name)
        if name == "": 
            return render_template("404.html",title="404 Not Found")
        try: 
            token = main.requestApiToken()
            get_artists = main.searchArtists(token, name)
        except: 
            return render_template("404.html",title="404 Not Found")
        return render_template("get_search.html",title="Search Artist",artists=get_artists,matched_artist=name)

@app.route("/get_top_tracks",methods=["POST","GET"])
def get_tracks():
    if request.method == "POST":
        top_tracks = request.form.get("search_tracks")
        if top_tracks == "": 
            return render_template("404.html",title="404 Not Found")
        try: 
            token = main.requestApiToken()
            get_tracks = main.get_top_tracks(token, top_tracks)
        except: 
            return render_template("404.html",title="404 Not Found")
        return render_template("top_tracks.html",title="Search Tracks",tracks=get_tracks,artist_title=top_tracks)


@app.route("/get_track_details",methods=["POST","GET"])
def get_track_details():
    if request.method == "POST":
        track_artist = request.form.get("search_details_artist")
        track_name = request.form.get("search_details_track")
        token = main.requestApiToken()
        get_tracks_details = main.searchSongDetails(token, track_name, track_artist)
        print(get_tracks_details)
        if get_tracks_details == None:
            return render_template("404.html",title="404 Not Found")
        return render_template("get_track_details.html", title="Search Tracks", tracks=get_tracks_details, artist=track_artist, name=track_name)
    


@app.route("/login",methods=["POST","GET"])
def addUserKey():
    if request.method=="POST":
        userAPIKey = request.form.get("user_api_key")
        return render_template("index.html")
    else:
        return render_template("login.html")


if __name__ == '__main__':
    app.run(host="192.168.2.252", debug=True, port=9191)