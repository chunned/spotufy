import requests
import dotenv


def requestApiToken():
    # Function to request an API token from Spotify - valid for 1hr

    # Read the app's client ID and secret from .env file
    apiSecrets = dotenv.dotenv_values('.env')

    apiUrl = "https://accounts.spotify.com/api/token"
    apiHeaders = {"Content-Type": "application/x-www-form-urlencoded"}
    apiData = {"grant_type": "client_credentials",
               "client_id": apiSecrets["CLIENT_ID"],
               "client_secret": apiSecrets["CLIENT_SECRET"]}

    response = requests.post(apiUrl, headers=apiHeaders, data=apiData)
    response = response.json()
    return response["access_token"]


