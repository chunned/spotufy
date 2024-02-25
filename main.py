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
        print('Reading .env file failed - no data read.\n'+
        'Ensure the .env file exists in the project root directory and contains the correct values\n'+
        'CLIENT_ID=<client id>\n'+
        'CLIENT_SECRET=<client secret>', end="")
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


def searchArtists(apiToken, artist):
    headers = {"Authorization": f"Bearer {apiToken}"}
    # URL encode artist string to ensure request executes properly
    query = urllib.parse.quote(artist)
    # Construct the query URL
    url = f"{APIURL}/search?q={query}&type=artist&limit=5"

    # Send the query - will return a list of matching artists
    try:
        response = requests.get(url, headers=headers)
        # If HTTP status code in response is anything other than 200 OK, raise an error
        response.raise_for_status()
        response = response.json()
        # Check if any artists were found during search
        if response['artists']['total'] == 0:
            raise ValueError("No search results found!")
    except requests.HTTPError as e:   # Catch non-200 status codes
        print(f"Error in API response code: {e}")
        exit(1)
    except ValueError as e:
        print(f"Error in search results: {e}")
        exit(1)

    # Construct search result output
    artists = ['']  # Will hold the artist results - insert one null value at index 0 for easier array access
    for artist in response['artists']['items']:
        artistResult = {
            "name": artist["name"],
            "url": artist["external_urls"]["spotify"],
            "followers": artist["followers"]["total"],
            "popularity": artist["popularity"],
            "genres": artist["genres"]
        }
        try:
            artistResult['imageUrl'] = artist["images"][0]["url"]
        except IndexError:
            artistResult['imageUrl'] = "Image not found"

        artists.append(artistResult)

    print("Displaying search results. Please select the matching artist.")
    # Iterate through artists, prompt user to select the correct one
    for i in range(1, len(artists)):
        print(f"RESULT #{i}\n"
            f"NAME: {artists[i]['name']}\n"
            f"URL: {artists[i]['url']}\n"
            f"FOLLOWERS: {artists[i]['followers']}\n"
            f"GENRE(s): {artists[i]['genres']}\n"
            f"PHOTO: {artists[i]['imageUrl']}\n---")