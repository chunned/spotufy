from flask import Flask,url_for,request,render_template
app = Flask(__name__)
import main

@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")

@app.route("/search",methods=["POST","GET"])
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
        return render_template("search.html",title="Search Artist",artists=get_artists)

@app.route("/login",methods=["POST","GET"])
def addUserKey():
    if request.method=="POST":
        userAPIKey = request.form.get("user_api_key")
        return render_template("index.html")
    else:
        return render_template("login.html")

if __name__ == '__main__':
    app.run(host="192.168.2.252", debug=True, port=9191)