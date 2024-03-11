import requests
import dotenv
import urllib.parse
import json
import base64
import webbrowser

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

    client_id = apiSecrets["CLIENT_ID"]
    client_secret = apiSecrets["CLIENT_SECRET"]
    try:
        # Authorize with relevant scopes
        # Authorization method adapted from https://python.plainenglish.io/bored-of-libraries-heres-how-to-connect-to-the-spotify-api-using-pure-python-bd31e9e3d88a
        scope = 'playlist-modify-public user-top-read'
        params = {
            'response_type': 'code',
            'client_id': client_id,
            'scope': scope,
            'redirect_uri': 'https://chunned.github.io/test/login-success'
        }
        webbrowser.open("https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(params))
        code = input("Enter the code from the end of the URL: ")
        #if len(code) != 224:
            #raise ValueError
    except ValueError:
        print("Invalid authorization code length. Please try again and make sure you copy the full code.")
        return None


    try:
        apiUrl = "https://accounts.spotify.com/api/token"
        encodedCreds = base64.b64encode(client_id.encode() + b':' + client_secret.encode()).decode("utf-8")
        apiHeaders = {"Content-Type": "application/x-www-form-urlencoded",
                      "Authorization": "Basic " + encodedCreds}
        apiData = {
            "grant_type": 'authorization_code',
            "code": code,
            "redirect_uri": "https://chunned.github.io/test/login-success"
        }

        resp = requests.post(url=apiUrl, data=apiData, headers=apiHeaders)
        # Bytes to dict solution from https://stackoverflow.com/questions/49184578/how-to-convert-bytes-type-to-dictionary
        data = json.loads(resp.content.decode('utf-8'))
        return data["access_token"]
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

def getUserRecs(apiToken):
    # URL encode username strings to ensure request executes properly
    headers = {"Authorization": f"Bearer {apiToken}"}
    # Construct the query URL to search for a user's top 5 tracks in the past 4 weeks
    url = f"{APIURL}/me/top/tracks?time_range=short_term&limit=5"
    try:
        response = makeApiCall(url, "GET", headers=headers)
        if not response:
            print("ERROR: Response from API request is empty")
            return None
        if response['total']== 0:
            print("ERROR: No track matching search creteria found")
            return None
    except ValueError as e:
        print(f"ERROR: Error in search results: {e}")
        return None

    #Parse through the json from the response given above to pinpoint the track id's of each song then add them to a string
    seed_tracks= ""
    for i in range(0, 5):
        x = response['items'][i]['id']
        seed_tracks = str(seed_tracks) + str(x)
        if i < 4:
            seed_tracks = str(seed_tracks) + ','
    print(seed_tracks)

    #URL Encode the string of tracks to ensure the request will process
    track_query = urllib.parse.quote(seed_tracks)
    url = f"{APIURL}/recommendations?limit=5&seed_tracks={track_query}"
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

    recs = ['']  # Will hold the track reccomendation results
    for rec in response['tracks']:
        #stores track id, album, artist and album art in dictionary
        recsResult = {
            "id": rec["id"],
            "name": rec["name"],
            "album": rec["album"]["name"],
            "artist": rec["artists"][0]["name"]
        }
        try:
            recsResult['imageUrl'] = rec["album"]["images"][0]["url"]
        except IndexError:
            recsResult['imageUrl'] = "Image not found"
        recs.append(recsResult)
    
    #prints the results of the dictionary for each track reccomendation.
    for i in range(1, len(recs)):
        print(f"RECOMMENDATION #{i}\n"
              f"NAME: {recs[i]['name']}\n"
              f"TRACK ID: {recs[i]['id']}\n"
              f"ARTIST: {recs[i]['artist']}\n"
              f"ALBUM: {recs[i]['album']}\n"
              f"PHOTO: {recs[i]['imageUrl']}\n---")

    return recs

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
    print(response)
    
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
    
    recs = ['']  # Will hold the track reccomendation results
    for rec in response['tracks']:
        #stores track id, album, artist and album art in dictionary
        recsResult = {
            "id": rec["id"],
            "name": rec["name"],
            "album": rec["album"]["name"],
            "artist": rec["artists"][0]["name"]
        }
        try:
            recsResult['imageUrl'] = rec["album"]["images"][0]["url"]
        except IndexError:
            recsResult['imageUrl'] = "Image not found"
        recs.append(recsResult)
    
    #prints the results of the dictionary for each track reccomendation.
    for i in range(1, len(recs)):
        print(f"RECOMMENDATION #{i}\n"
              f"NAME: {recs[i]['name']}\n"
              f"TRACK ID: {recs[i]['id']}\n"
              f"ARTIST: {recs[i]['artist']}\n"
              f"ALBUM: {recs[i]['album']}\n"
              f"PHOTO: {recs[i]['imageUrl']}\n---")

    return recs
    