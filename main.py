import requests
import dotenv
import urllib.parse
import json

APIURL = "https://api.spotify.com/v1"


def requestApiToken():
    # Function to request an API token from Spotify - valid for 1hr

    # Read the app's client ID and secret from .env file
    try:
        apiSecrets = dotenv.dotenv_values('.env')
        if not apiSecrets:
            raise ValueError
    except ValueError:
        print('Reading .env file failed - no data read.')
        print('Ensure the .env file exists in the project root directory and contains the correct values')
        print('CLIENT_ID=<client id>')
        print('CLIENT_SECRET=<client secret>')
        exit(1)

    try:
        apiUrl = "https://accounts.spotify.com/api/token"
        apiHeaders = {"Content-Type": "application/x-www-form-urlencoded"}
        apiData = {"grant_type": "client_credentials",
                   "client_id": apiSecrets["CLIENT_ID"],
                   "client_secret": apiSecrets["CLIENT_SECRET"]}

        response = requests.post(apiUrl, headers=apiHeaders, data=apiData)
        response = response.json()
        return response["access_token"]
    except KeyError:
        print('No access token found in API response. Ensure your CLIENT_ID and CLIENT_SECRET are correct.')
        exit(1)

