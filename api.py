from flask import Flask,url_for,request,render_template,redirect,session
import main
import dotenv
import urllib
import requests

def request_api_token():
    try:
        apiSecrets = dotenv.dotenv_values('.env')
        if not apiSecrets:
            raise ValueError
    except ValueError:
        print('Reading .env file failed - no data read.\n' +
              'Ensure the .env file exists in the project root directory and contains the correct values\n' +
              'CLIENT_ID=<client id>\n' +
              'CLIENT_SECRET=<client secret>', end="")
        return None

    client_id = apiSecrets["CLIENT_ID"]
    client_secret = apiSecrets["CLIENT_SECRET"]
    
    scope = 'playlist-modify-public playlist-modify-private'
    params = {
            'response_type': 'code',
            'client_id': client_id,
            'scope': scope,
            'redirect_uri': 'http://192.168.2.252:9191/callback',
            "show_dialog" : True
        }
    SITE_URL = "https://accounts.spotify.com/authorize"
    auth_url = f"{SITE_URL}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)
