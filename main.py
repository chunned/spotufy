import requests
import dotenv
import urllib.parse
import re
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
    except requests.exceptions.MissingSchema as e:
        print(f"ERROR: Missing schema info. Ensure the URL is valid: {e}")
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
        print('Reading .env file failed - no data read.\n' +
              'Ensure the .env file exists in the project root directory and contains the correct values\n' +
              'CLIENT_ID=<client id>\n' +
              'CLIENT_SECRET=<client secret>', end="")
        return None

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
        return None


def searchArtists(apiToken, artist):
    headers = {"Authorization": f"Bearer {apiToken}"}
    # URL encode artist string to ensure request executes properly
    query = urllib.parse.quote(artist)
    # Construct the query URL
    url = f"{APIURL}/search?q={query}&type=artist&limit=5"

    artist = parseInput(artist)

    # Send the query - will return a list of matching artists
    try:
        response = makeApiCall(url, "GET", headers=headers)

        if not response:
            print("ERROR: Response from API request is empty")
            return None
        # Check if any artists were found during search
        if response['artists']['total'] == 0:
            raise ValueError("No search results found!")
    except ValueError as e:
        print(f"ERROR: Error in search results: {e}")
        return None

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

    userChoice = input("Enter the result you would like to select: ")
    try:
        userChoice = int(userChoice)
    except ValueError as e:
        print(f'ERROR: Invalid input value. Please try again, entering an integer. {e}')
        return None

    try:
        return artists[userChoice]
    except IndexError as e:
        print("ERROR: Invalid choice - please try again and make sure you enter a number corresponding to the search "
              "results.")
        return None


def searchSongDetails(apiToken, track, artist):
    if track == "":
        print("ERROR: Track input is empty")
        return None
    if artist == "":
        print("ERROR: Artist input is empty")
        return None

    track = parseInput(track)
    artist = parseInput(artist)

    # URL encode track and artist strings to ensure request executes properly
    track_query = urllib.parse.quote(track)
    artist_query = urllib.parse.quote(artist)
    headers = {"Authorization": f"Bearer {apiToken}"}

    # Construct the query URL
    url = f"{APIURL}/search?q=track%3A{track_query}+artist%3A{artist_query}&type=track&limit=1"
    response = makeApiCall(url, "GET", headers=headers)
    if not response:
        print("ERROR: Response from API request is empty")
        return None
    if not response["tracks"]["items"]:
        print("ERROR: No track matching search criteria found")
        return None
    # Parse API response and store track information
    track = response["tracks"]["items"][0]
    print(json.dumps(track, indent=2))
    trackResults = {
        "name": track["name"],
        "album": track["album"]["name"],
        "artist": track["album"]["artists"][0]["name"],
        "duration": track["duration_ms"] * (10 ** -3),
        "released": track["album"]["release_date"],
        "url": track["external_urls"]["spotify"],
    }
    try:
        trackResults['image'] = track["album"]["images"][1]["url"]
    except IndexError:
        trackResults['image'] = "Image not found"
    return trackResults

# Example of working URI for searching a song: 
# https://api.spotify.com/v1/search?q=track%3AStars+artist%3ASkillet&type=track&limit=5


def parseInput(string):
    # Remove any non-alphanumeric, non-space characters from input to prevent search from failing
    # Solution from https://stackoverflow.com/questions/3939361/remove-specific-characters-from-a-string-in-python
    return re.sub('[^0-9a-zA-Z ]', '', string)


tok = requestApiToken()
song = searchSongDetails(tok, "Thief's Theme", "N@#$@#$@#$a%(@$)@#%s")
#print(json.dumps(song, indent=2))