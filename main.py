import requests
import dotenv
import urllib.parse
import re
import json
import base64
import webbrowser

APIURL = 'https://api.spotify.com/v1'

def makeApiCall(url, method, headers=None, payload=None):
    # Generalized function to make any and all API requests as needed by the application

    # Send the request with the passed in parameters
    try:
        response = requests.request(method, url, headers=headers, data=payload)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"ERROR: Error in API response code: {e}")
        return None
    except requests.exceptions.MissingSchema as e:
        print(f"ERROR: Missing schema info. Ensure the URL is valid: {e}")
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
        scope = 'playlist-modify-public playlist-modify-private'
        params = {
            'response_type': 'code',
            'client_id': client_id,
            'scope': scope,
            'redirect_uri': 'https://chunned.github.io/test/login-success'
        }
        webbrowser.open("https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(params))
        code = input("Enter the code from the end of the URL: ")
    except ValueError:
        print("Invalid authorization code length. Please try again and make sure you copy the full code.")
        return None

    try:
        apiUrl = "https://accounts.spotify.com/api/token"
        encodedCreds = base64.b64encode(client_id.encode() + b':' + client_secret.encode()).decode("utf-8")
        apiHeaders = {"Content-Type": "application/x-www-form-urlencoded",
                      "Authorization": "Basic " + encodedCreds}
        apiData = {
            "grant_type": "authorization_code",
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

def searchArtists(apiToken, inputArtist):
    headers = {"Authorization": f"Bearer {apiToken}"}
    # URL encode artist string to ensure request executes properly
    query = urllib.parse.quote(inputArtist)
    # Construct the query URL
    url = f"{APIURL}/search?q={query}&type=artist&limit=5"
    artist = parseInput(inputArtist)

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
    # For details on enumerate() see https://realpython.com/python-enumerate/
    for i, artist in enumerate(response['artists']['items']):
        artistResult = {
            "name": artist["name"],
            "url": artist["external_urls"]["spotify"],
            "followers": artist["followers"]["total"],
            "popularity": artist["popularity"],
            "genres": artist["genres"],
            "id": artist["id"]
        }
        try:
            artistResult['imageUrl'] = artist["images"][0]["url"]
        except IndexError:
            artistResult['imageUrl'] = "Image not found"
        finally:
            if i == 0 and artistResult['name'].lower() == inputArtist.lower():
                # If the first result matches exactly the input search string, we can assume it is the correct
                # artist, so return it. Otherwise, iterate through results
                return artistResult
            else:
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

def parseInput(string):
    # Remove any non-alphanumeric, non-space characters from input to prevent search from failing
    # Solution from https://stackoverflow.com/a/46414390
    return re.sub('[^0-9a-zA-Z ]', '', string)

def getArtistReleases(apiToken, artist):
    # Query all artist releases
    # artist should be an artist dictionary returned from searchArtists()
    try:
        artist_id = artist['id']
    except (KeyError, TypeError):
        print("ERROR: No artist ID found. Ensure you are passing a valid artist dictionary object from searchArtist()")
        return None

    headers = {"Authorization": f"Bearer {apiToken}"}
    url = f"{APIURL}/artists/{artist_id}/albums?limit=50"

    try:
        response = makeApiCall(url, "GET", headers=headers)
        if not response:
            print("ERROR: Response from API request is empty")
            return None
        # Check if any releases were found during search
        if response['total'] == 0:
            raise ValueError("No releases found for this artist!")
    except ValueError as e:
        print(f"ERROR: Error in search results: {e}")
        return None

    releases = []
    for release in response['items']:
        releaseItem = {
            "type": release["album_group"],
            "url": release["external_urls"]["spotify"],
            "album_id": release["id"],
            "album_artists": [a for a in release['artists']],
            "title": release["name"],
            "release_date": release["release_date"],
            "tracks": release["total_tracks"]
        }
        try:
            releaseItem["cover_image"] = release["images"][0]["url"]
        except IndexError:
            releaseItem["cover_image"] = "Image not found"
        finally:
            releases.append(releaseItem)
    return releases


def create_playlist(api_token, playlist_name, track_list):
    headers = {"Authorization": f"Bearer {api_token}", "Content-Type":"application/json"}
    url = "https://api.spotify.com/v1/me"
    try:
        user_id = makeApiCall(url, "GET", headers=headers)["id"]
    except TypeError:
        print('ERROR: No valid user ID returned. Ensure your authorization token is correct.')
    playlist_id = ""
    # Send the POST query to create the playlist. Will create a playlist for later inserting tracks into
    try:
        if playlist_name:
            data = {
                "name": playlist_name,
                "description": "New playlist description",
            }
            payloaddump = json.dumps(data)
            url = f"{APIURL}/users/{user_id}/playlists"
            response = makeApiCall(url, "POST", headers=headers, payload=payloaddump)
            if not response:
                print("ERROR: Response from API request is empty")
                return None
            playlist_id = response["id"]
        else:
            raise ValueError("No playlist name provided")
    except ValueError as e:
        print(f'ERROR: {e}'
              )
    try:
        if playlist_id:
            # Send the POST query to insert tracks into the newly created playlist
            url = f"{APIURL}/playlists/{playlist_id}/tracks"
            data = {"uris": [track["uri"] for track in track_list]}
            data = json.dumps(data, indent=2)
            response = makeApiCall(url, "POST", headers=headers, payload=data)
            if not response:
                raise ValueError("No response from API query. Ensure track URIs are correct.")
        else:
          raise ValueError("No playlist ID returned")
    except ValueError as e:
        print(f'ERROR: {e}')
def getRelatedArtists(apiToken, artistID):
    # artistID can be obtained from the dictionary returned by searchArtists()

    headers = {"Authorization": f"Bearer {apiToken}"}
    # URL encode artist string to ensure request executes properly
    query = urllib.parse.quote(artistID)
    # Construct the query URL
    url = f"{APIURL}/artists/{artistID}/related-artists"

    try:
        response = makeApiCall(url, "GET", headers=headers)
        # print(json.dumps(response, indent=2))
        if not response:
            print("ERROR: Response from API request is empty")
            return None

        # Check if any artists were found during search
        if len(response['artists']) == 0:
            raise ValueError("No search results found!")

    except ValueError as e:
        print(f"ERROR: Error in search results: {e}")
        return None

    relatedArtists = []
    for artistResult in response['artists']:
        a = searchArtists(apiToken, artistResult['name'])
        relatedArtists.append(a)

    return relatedArtists


token = requestApiToken()

a = {"uri": "spotify:track:a"}
b = {"uri": "spotify:track:bi"}

res = create_playlist(token, "#%asdfasdfasdf~%$#%", [a, b])

