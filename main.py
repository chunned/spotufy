import requests
import dotenv
import urllib.parse
import json

APIURL = 'https://api.spotify.com/v1'

def makeApiCall(url, method, headers=None, paylode=None):
    # Generalized function to make any and all API requests as needed by the application

    # Send the request with the passed in parameters
    try:
        response = requests.request(method, url, headers=headers, data=paylode)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"ERROR: Error in API response code: {e}")
        return None
    else: 
        return response.json() if response.text else None

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

        response = makeApiCall(apiUrl, "POST", headers=apiHeaders, paylode=apiData)
        return response["access_token"]
    except KeyError:
        print('ERROR: No access token found in API response. Ensure your CLIENT_ID and CLIENT_SECRET are correct.')
        exit(1)


def searchArtists(apiToken, artist):
    headers = {"Authorization": f"Bearer {apiToken}"}
    # URL encode artist string to ensure request executes properly
    query = urllib.parse.quote(artist)
    # Construct the query URL
    url = f"{APIURL}/search?q={query}&type=artist&limit=5"

    # Send the query - will return a list of matching artists
    try:
        response = makeApiCall(url, "GET", headers=headers)

        if not response:
            print("ERROR: Response from API request is empty")
            exit(1)
        # Check if any artists were found during search
        if response['artists']['total'] == 0:
            raise ValueError("No search results found!")
    except ValueError as e:
        print(f"ERROR: Error in search results: {e}")
        exit(1)

    # Construct search result output
    artists = ['']  # Will hold the artist results - insert one null value at index 0 for easier array access
    for artist in response['artists']['items']:
        artistResult = {
            "name": artist["name"],
            "url": artist["external_urls"]["spotify"],
            "followers": artist["followers"]["total"],
            "popularity": artist["popularity"],
            "genres": artist["genres"],
            "id" : artist["id"]
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
              f"ID: {artists[i]['id']}\n"
            f"NAME: {artists[i]['name']}\n"
            f"URL: {artists[i]['url']}\n"
            f"FOLLOWERS: {artists[i]['followers']}\n"
            f"GENRE(s): {artists[i]['genres']}\n"
            f"PHOTO: {artists[i]['imageUrl']}\n---")
    return artists

def get_top_tracks(apiToken,artist_name):
    artists_got = searchArtists(apiToken,artist_name)
    artist_id = artists_got[1]["id"]
    headers = {"Authorization": f"Bearer {apiToken}"}
    # URL encode artist string to ensure request executes properly
    query = urllib.parse.quote(artist_id)
    # Construct the query URL
    url = f"{APIURL}/artists/{query}/top-tracks?market=US&limit=5"

    # Send the query - will return a list of matching artists
    try:
        response = makeApiCall(url, "GET", headers=headers)

        if not response:
            print("ERROR: Response from API request is empty")
            exit(1)
        # Check if any artists were found during search
        if response['tracks'] == 0:
            raise ValueError("No search results found!")
    except ValueError as e:
        print(f"ERROR: Error in search results: {e}")
        exit(1)

    tracks = []
    for track in response['tracks']:
        artistResult = {
            "name": track["name"],
            "album" : track["album"]["name"],
            "albumDate" : track["album"]["release_date"],
            "albumImage" : track["album"]["images"][1]["url"],
            "songUrl" : track["external_urls"]["spotify"],
            "popularity": track["popularity"]
        }
        tracks.append(artistResult)

    for i in range(1, len(tracks)):
        print(
              f"name: {tracks[i]['name']}\n"
              f"album: {tracks[i]['album']}\n"
              f"albumDate: {tracks[i]['albumDate']}\n"
              f"albumImage: {tracks[i]['albumImage']}\n"
              f"songUrl: {tracks[i]['songUrl']}\n"
              f"popularity: {tracks[i]['popularity']}\n"
        )
    return tracks
