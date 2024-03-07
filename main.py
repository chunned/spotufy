import requests
import dotenv
import urllib.parse
import json
import prettyprint as pp

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
            "genres": artist["genres"],
            "id" : artist["id"],
            "uri" : artist["uri"]
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
            f"PHOTO: {artists[i]['imageUrl']}\n"
            f"SPOTIFYURI: {artists[i]['uri']}\n---")
    return artists

def searchSongDetails(apiToken, track, artist):
    if track == "":
        print("ERROR: Track input is empty")
        return None
    if artist == "":
        print("ERROR: Artist input is empty")
        return None
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
    if response["tracks"]["items"] == []:
        print("ERROR: No track matching search creteria found")
        return None
    # Parse API response and store track information
    track = response["tracks"]["items"][0]
    trackResults = {
        "id" : track["id"],
        "name": track["name"],
        "album": track["album"]["name"],
        "artist": track["album"]["artists"][0]["name"],
        "duration": str(round(track["duration_ms"] * (10**-3),0)),
        "released": track["album"]["release_date"],
        "url": track["external_urls"]["spotify"],
        "uri" : track["uri"]
    }
    try:
        trackResults['image'] = track["album"]["images"][1]["url"]
    except IndexError:
        trackResults['image'] = "Image not found"
    for i in trackResults.values(): #remove print later 
        print(i)
    return trackResults
    
# Example of working URI for searching a song: 
# https://api.spotify.com/v1/search?q=track%3AStars+artist%3ASkillet&type=track&limit=5   

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

    top_tracks = []
    for track in response['tracks']:
        artistResult = {
            "name": track["name"],
            "album" : track["album"]["name"],
            "albumDate" : track["album"]["release_date"],
            "albumImage" : track["album"]["images"][1]["url"],
            "songUrl" : track["external_urls"]["spotify"],
            "popularity": track["popularity"],
            "uri" : track["uri"]
        }
        top_tracks.append(artistResult)

    for i in range(1, len(top_tracks)):
        print(
              f"name: {top_tracks[i]['name']}\n"
              f"album: {top_tracks[i]['album']}\n"
              f"albumDate: {top_tracks[i]['albumDate']}\n"
              f"albumImage: {top_tracks[i]['albumImage']}\n"
              f"songUrl: {top_tracks[i]['songUrl']}\n"
              f"popularity: {top_tracks[i]['popularity']}\n"
              f"spotifyuri: {top_tracks[i]['uri']}\n"
        )
    return top_tracks

def getTrackRecs(apiToken, track, artist):
    # URL encode track and artist strings to ensure request executes properly
    track_query = urllib.parse.quote(track)
    artist_query = urllib.parse.quote(artist)
    headers = {"Authorization": f"Bearer {apiToken}"}
    # Construct the query URL to search for specified track by specified artist
    url = f"{APIURL}/search?q=track%3A{track_query}+artist%3A{artist_query}&type=track&limit=1"
    try:
        response = makeApiCall(url, "GET", headers=headers)
        if not response:
            print("ERROR: Response from API request is empty")
            return None
        if response["tracks"]["items"] == []:
            print("ERROR: No track matching search creteria found")
            return None
    except ValueError as e:
        print(f"ERROR: Error in search results: {e}")
        return None
    
    # Parse API response and stores track id
    track = response["tracks"]["items"][0]
    trackID = track["id"]

    # Construct the query URL to search for the top 5 reccomended tracks based on specified track id
    rec_query = urllib.parse.quote(trackID)
    url = f"{APIURL}/recommendations?limit=5&seed_tracks={rec_query}"
    try:
        response = makeApiCall(url, "GET", headers=headers)
        if not response:
            print("ERROR: Response from API request is empty")
            return None
        if response["tracks"][0] == []:
            print("ERROR: No track matching search creteria found")
            return None
    except ValueError as e:
        print(f"ERROR: Error in search results: {e}")
        return None
    
    recs = ['']  # Will hold the track reccomendation results - insert one null value at index 0 for easier array access
    for rec in response['tracks']:
        #stores track id, album, artist and album art in dictionary
        recsResult = {
            "id": rec["id"],
            "name": rec["name"],
            "album": rec["album"]["name"],
            "artist": rec["artists"][0]["name"],
            "popularity" : rec["popularity"],
            "songUrl" : rec["external_urls"]["spotify"],
            "uri" : rec["uri"]
        }
        try:
            recsResult['imageUrl'] = rec["album"]["images"][0]["url"]
        except IndexError:
            recsResult['imageUrl'] = "Image not found"
        recs.append(recsResult)

    urlPlaylist = f"{APIURL}/users/31vhpkpydirwzkgleucf36ec2aba/playlists"
    apiHeaders = {"Content-Type": "application/json",
                  "Authorization": f"Bearer {apiToken}"}
    data = json.dumps({
        "name": "Test Playlist",
        "description": "Playlist",
        "public" : True
    })
    
    responsePlaylist = makeApiCall(urlPlaylist, "POST", headers=apiHeaders,paylode=data)
    print(responsePlaylist)
    return recs