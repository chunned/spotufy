import requests
import dotenv
import urllib.parse
import re
import json
import lyricsgenius
from flask import redirect

# Base API URL used for all API requests
APIURL = 'https://api.spotify.com/v1'


################ Core Functions ################
# These functions do not constitute features,  #
# but are used by the functions that make up   #
# the features.                                #
################################################

def make_api_call(url, method, headers=None, payload=None):
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

def request_api_token():
    # Function to request an API token from Spotify - valid for 1hr
    # Read the app's client ID and secret from .env file
    try:
        api_secrets = dotenv.dotenv_values('.env')
        if not api_secrets:
            raise ValueError
    except ValueError:
        print('Reading .env file failed - no data read.\n' +
              'Ensure the .env file exists in the project root directory and contains the correct values\n' +
              'CLIENT_ID=<client id>\n' +
              'CLIENT_SECRET=<client secret>', end="")
        return None

    client_id = api_secrets["CLIENT_ID"]

    # Scopes define what permissions the application has to perform on a user's behalf.
    # Read more: https://developer.spotify.com/documentation/web-api/concepts/scopes
    scope = 'playlist-modify-public playlist-modify-private user-top-read'
    params = {
            'response_type': 'code',
            'client_id': client_id,
            'scope': scope,
            'redirect_uri': api_secrets["CALLBACK_URL"],
            "show_dialog" : True
        }
    SITE_URL = "https://accounts.spotify.com/authorize"
    auth_url = f"{SITE_URL}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)

def parse_input(string):
    # Remove any non-alphanumeric, non-space characters from input to prevent search from failing
    # Solution from https://stackoverflow.com/a/46414390
    return re.sub('[^0-9a-zA-Z ]', '', string)

def create_playlist(api_token, playlist_name, track_list):
    headers = {"Authorization": f"Bearer {api_token}", "Content-Type":"application/json"}
    url = "https://api.spotify.com/v1/me"
    user_id = make_api_call(url, "GET", headers=headers)["id"]

    # Send the POST query to create the playlist. Will create a playlist for later inserting tracks into
    data = {
        "name": playlist_name,
        "description": "Playlist created by SpOTUfy!",
    }
    payload = json.dumps(data)
    url = f"{APIURL}/users/{user_id}/playlists"
    response = make_api_call(url, "POST", headers, payload)
    if not response:
        return None
    playlist_id = response["id"]
    play_url = response["external_urls"]["spotify"]

    # Send the POST query to insert tracks into the newly created playlist
    url = f"{APIURL}/playlists/{playlist_id}/tracks"
    track_data = {"uris": [track["uri"] for track in track_list]}
    track_payload = json.dumps(track_data)
    response = make_api_call(url, "POST", headers, track_payload)
    if not response:
        return None
    else:
        return play_url


################ Feature Functions ################

def search_artists(api_token, input_artist):
    # Searches artist by name and returns a list of matches
    headers = {"Authorization": f"Bearer {api_token}"}
    # URL encode artist string to ensure request executes properly
    artist = parse_input(input_artist)
    query = urllib.parse.quote(artist)
    # Construct the query URL
    url = f"{APIURL}/search?q={query}&type=artist&limit=5"

    # Send the query - will return a list of matching artists
    try:
        response = make_api_call(url, "GET", headers)

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
        artist_result = {
            "name": artist["name"],
            "url": artist["external_urls"]["spotify"],
            "followers": "{:,d}".format(artist["followers"]["total"]),
            "popularity": artist["popularity"],
            "genres": ', '.join(artist["genres"]), 
            "id" : artist["id"],
            "uri" : artist["uri"]
        }
        try:
            artist_result['imageUrl'] = artist["images"][0]["url"]
        except IndexError:
            artist_result['imageUrl'] = "Image not found"
        artists.append(artist_result)
    return artists

def get_top_tracks(apiToken, artist_name):
    # Get the most popular tracks for a given artist
    artists_got = search_artists(apiToken, artist_name)
    try:
        artist_id = artists_got[1]["id"]
    except TypeError:
        print("ERROR: Artist was not found.")
        return None
    headers = {"Authorization": f"Bearer {apiToken}"}
    # URL encode artist string to ensure request executes properly
    query = urllib.parse.quote(artist_id)
    # Construct the query URL
    url = f"{APIURL}/artists/{query}/top-tracks?market=US&limit=5"

    # Send the query - will return a list of matching artists
    try:
        response = make_api_call(url, "GET", headers=headers)

        if not response:
            print("ERROR: Response from API request is empty")
            return None
        # Check if any artists were found during search
        if response['tracks'] == 0:
            raise ValueError("No search results found!")
    except ValueError as e:
        print(f"ERROR: Error in search results: {e}")
        return None

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
    return top_tracks

def search_song_details(api_token, track, artist):
    # Return information about a given track
    if track == "":
        print("ERROR: Track input is empty")
        return None
    if artist == "":
        print("ERROR: Artist input is empty")
        return None

    track = parse_input(track)
    artist = parse_input(artist)

    # URL encode track and artist strings to ensure request executes properly
    track_query = urllib.parse.quote(track)
    artist_query = urllib.parse.quote(artist)
    headers = {"Authorization": f"Bearer {api_token}"}

    # Construct the query URL
    url = f"{APIURL}/search?q=track%3A{track_query}+artist%3A{artist_query}&type=track&limit=1"
    response = make_api_call(url, "GET", headers)
    if not response:
        print("ERROR: Response from API request is empty")
        return None
    if not response["tracks"]["items"]:
        print("ERROR: No track matching search criteria found")
        return None
    # Parse API response and store track information
    track = response["tracks"]["items"][0]
    track_results = {
        "id" : track["id"],
        "name": track["name"],
        "album": track["album"]["name"],
        "artist": track["album"]["artists"][0]["name"],
        "duration": track["duration_ms"] * (10 ** -3),
        "released": track["album"]["release_date"],
        "url": track["external_urls"]["spotify"],
    }
    try:
        track_results['image'] = track["album"]["images"][1]["url"]
    except IndexError:
        track_results['image'] = "Image not found"
    return track_results

def get_track_recs(apiToken, track, artist):
    # Get a list of recommended tracks based on a single input track
    # URL encode track and artist strings to ensure request executes properly
    track_query = urllib.parse.quote(track)
    artist_query = urllib.parse.quote(artist)
    headers = {"Authorization": f"Bearer {apiToken}"}
    # Construct the query URL to search for specified track by specified artist
    url = f"{APIURL}/search?q=track%3A{track_query}+artist%3A{artist_query}&type=track&limit=1"
    try:
        response = make_api_call(url, "GET", headers=headers)
        if not response:
            print("ERROR: Response from API request is empty")
            return None
        if not response["tracks"]["items"]:
            print("ERROR: No track matching search criteria found")
            return None
    except ValueError as e:
        print(f"ERROR: Error in search results: {e}")
        return None

    # Parse API response and stores track id
    track = response["tracks"]["items"][0]
    trackID = track["id"]

    # Construct the query URL to search for the top 5 recommended tracks based on specified track id
    rec_query = urllib.parse.quote(trackID)
    url = f"{APIURL}/recommendations?limit=5&seed_tracks={rec_query}"
    try:
        response = make_api_call(url, "GET", headers=headers)
        if not response:
            print("ERROR: Response from API request is empty")
            return None
        if not response["tracks"][0]:
            print("ERROR: No track matching search criteria found")
            return None
    except ValueError as e:
        print(f"ERROR: Error in search results: {e}")
        return None

    recs = []  # Will hold the track recommendation results - insert one null value at index 0 for easier array access
    for rec in response['tracks']:
        # Stores track id, album, artist and album art in dictionary
        recs_result = {
            "id": rec["id"],
            "name": rec["name"],
            "album": rec["album"]["name"],
            "artist": rec["artists"][0]["name"],
            "popularity" : rec["popularity"],
            "songUrl" : rec["external_urls"]["spotify"],
            "uri" : rec["uri"]
        }
        try:
            recs_result['imageUrl'] = rec["album"]["images"][0]["url"]
        except IndexError:
            recs_result['imageUrl'] = "Image not found"
        recs.append(recs_result)
    return recs

def get_user_recs(api_token):
    # Get recommendations based on user's top tracks
    # URL encode username strings to ensure request executes properly
    headers = {"Authorization": f"Bearer {api_token}"}
    # Construct the query URL to search for a user's top 5 tracks in the past 4 weeks
    url = f"{APIURL}/me/top/tracks?time_range=short_term&limit=5"
    try:
        response = make_api_call(url, "GET", headers=headers)
        if not response:
            print("ERROR: Response from API request is empty")
            return None
        if response['total']== 0:
            print("ERROR: No track matching search criteria found")
            return None
    except ValueError as e:
        print(f"ERROR: Error in search results: {e}")
        return None

    # Parse through the json from the response given above to pinpoint the track id's of each song then add them to a string
    seed_tracks= ""
    for i in range(0, 5):
        x = response['items'][i]['id']
        seed_tracks = str(seed_tracks) + str(x)
        if i < 4:
            seed_tracks = str(seed_tracks) + ','

    # URL Encode the string of tracks to ensure the request will process
    track_query = urllib.parse.quote(seed_tracks)
    url = f"{APIURL}/recommendations?limit=5&seed_tracks={track_query}"
    try:
        response = make_api_call(url, "GET", headers=headers)
        if not response:
            print("ERROR: Response from API request is empty")
            return None
        if not response["tracks"][0]:
            print("ERROR: No track matching search criteria found")
            return None
    except ValueError as e:
        print(f"ERROR: Error in search results: {e}")
        return None

    recs = ['']  # Will hold the track recommendation results
    for rec in response['tracks']:
        # Stores track id, album, artist and album art in dictionary
        recs_result = {
            "id": rec["id"],
            "name": rec["name"],
            "album": rec["album"]["name"],
            "artist": rec["artists"][0]["name"],
            "popularity" : rec["popularity"],
            "songUrl" : rec["external_urls"]["spotify"],
            "uri" : rec["uri"]
        }
        try:
            recs_result['imageUrl'] = rec["album"]["images"][0]["url"]
        except IndexError:
            recs_result['imageUrl'] = "Image not found"
        recs.append(recs_result)
    return recs

def get_related_artists(api_token, artist_id):
    # Search for artists related to a given input artist and return matching results
    # artistID can be obtained from the dictionary returned by search_artists()

    headers = {"Authorization": f"Bearer {api_token}"}
    # Construct the query URL
    url = f"{APIURL}/artists/{artist_id}/related-artists"

    try:
        response = make_api_call(url, "GET", headers)
        if not response:
            print("ERROR: Response from API request is empty")
            return None

        # Check if any artists were found during search
        if len(response['artists']) == 0:
            raise ValueError("No search results found!")
    except ValueError as e:
        print(f"ERROR: Error in search results: {e}")
        return None
    related_artists = []
    for artist_result in response['artists']:
        a = search_artists(api_token, artist_result['name'])
        related_artists.append(a)
    return related_artists

def get_genius_lyrics(artist_name, track_name):
    # Retrieve Genius.com lyrics using lyricsgenius package
    secrets = dotenv.dotenv_values('.env')
    genius_token = secrets["GENIUS_TOKEN"]
    genius = lyricsgenius.Genius(genius_token)
    genius.response_format = 'html'

    try:
        if not isinstance(artist_name, str):
            raise TypeError("Invalid artist name type. Make sure artist name is a string.")
        if not isinstance(track_name, str):
            raise TypeError("Invalid track name type. Make sure track name is a string.")
        if not artist_name:
            raise ValueError("No artist name included in search")
        if track_name:
            song = genius.search_song(track_name, artist_name)
        else:
            raise ValueError("No track name included in search")
        if song:
            lyrics = song.lyrics
            lyrics = lyrics.split('\n')
            lyrics = '\n'.join(lyrics[1:])
            return lyrics
        else:
            return None
    except ValueError as e:
        print(f'ERROR: {e}')
        return None
    except AttributeError as e:
        print(f'ERROR: Invalid input artist/track. {e}')
        return None
    except TypeError as e:
        print(f'ERROR: {e}')
        return None

def get_artist_releases(api_token, artist):
    # Query all artist releases
    # artist should be an artist dictionary returned from searchArtists()
    try:
        artist_id = artist['id']
    except KeyError:
        print("ERROR: No artist ID found. Ensure you are passing a valid artist dictionary object from searchArtist()")
        return None
    except TypeError:
        print("ERROR: Input artist is not a valid artist dictionary.")
        return None

    headers = {"Authorization": f"Bearer {api_token}"}
    url = f"{APIURL}/artists/{artist_id}/albums?limit=50"

    try:
        response = make_api_call(url, "GET", headers=headers)
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