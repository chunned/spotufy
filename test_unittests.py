import unittest
from spotufy import *
import base64
from app import app
import webbrowser

def testing_request_api_token(flask_app):
    # Authorization flow requires an HTTP callback
    # This test-specific setup function handles this flow without running app.py
    # This is a slightly modified version of spotufy.request_api_token() that doesn't use Flask

    app_client = flask_app.test_client()    # Create a Flask test client for the application
    api_secrets = dotenv.dotenv_values('.env')  # Read .env secrets
    client_id = api_secrets["CLIENT_ID"]
    client_secret = api_secrets["CLIENT_SECRET"]


    response = app_client.get('/login')
    auth_url = response.headers[2][1]        # Extract redirect URL from HTTP response headers
    # Open Spotify auth URL in web browser so user can authorize the app to act on their behalf
    webbrowser.open(auth_url)
    code = input("Enter the authorization code shown on the page: ")

    apiUrl = "https://accounts.spotify.com/api/token"
    encodedCreds = base64.b64encode(client_id.encode() + b':' + client_secret.encode()).decode("utf-8")
    apiHeaders = {"Content-Type": "application/x-www-form-urlencoded",
                  "Authorization": "Basic " + encodedCreds}
    apiData = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "https://chunned.github.io/test/index.html"
    }
    resp = requests.post(url=apiUrl, data=apiData, headers=apiHeaders)
    # Bytes to dict solution from https://stackoverflow.com/questions/49184578/how-to-convert-bytes-type-to-dictionary
    data = json.loads(resp.content.decode('utf-8'))
    return data['access_token']

token = testing_request_api_token(app)

class make_api_call_test(unittest.TestCase):
    """Test module to test API call function in `spotufy.py`"""
    def test_valid_return(self):
        """Function should return a JSON object if given valid input"""
        url = "https://api.spotify.com/v1/tracks/11dFghVXANMlKmJXsNCbNl"
        headers = {"Authorization": f"Bearer {token}"}
        self.assertTrue(type(make_api_call(url, "GET", headers)) == type({}))
    def test_HTTP_error_return(self):
        """Function should return None if an HTTP status code is raised"""
        url = "https://api.spotify.com/v1/tracks/11dFghVXANMlKmJXsNCbNl"
        # Invalid token, should raise a 401 error and return None
        headers = {"Authorization": f"Bearer wefoijweoijsxoijwed"}
        self.assertTrue(None==make_api_call(url, "GET", headers))
    def test_invalid_schema_return(self):
        """Function should return None if the schema of the URL is wrong/missing"""
        # URL missing schema, should raise exception and return None
        url = "api.spotify.com/v1/track/11dFghVXANMlKmJXsNCbNl"
        headers = {"Authorization": f"Bearer {token}"}
        self.assertTrue(None==make_api_call(url, "GET", headers))


class request_api_token_test(unittest.TestCase):
    """Test module to test request API token function in `spotufy.py`"""
    def test_token_received(self):
        """API token string should be returned and not be None"""
        self.assertTrue(None!=request_api_token())


class search_artists_test(unittest.TestCase):
    """Test module to test search artists function in `spotufy.py"""
    def test_valid_return(self):
        """Function should return a non-empty list if given good input"""
        self.assertTrue([]!=search_artists(token, "Al Green"))
    def test_invalid_return(self):
        """Function should return None if given bad input (no matching artist from search)"""
        self.assertTrue(None==search_artists(token, "sdfouhxiuheiuwer"))


class search_song_details_test(unittest.TestCase):
    """Test module to test search song details function in `spotufy.py`"""
    def test_blank_input(self):
        """Function should return None if given empty input"""
        self.assertTrue(None==search_song_details(token, "", ""))
    def test_no_match(self):
        """Function should return None if there is no matching result from API"""
        self.assertTrue(None==search_song_details(token, "Banana Pop Bozo", "Frisbee Cube Clock"))
    def test_valid_return(self):
        """Function should return a dictionary of track information if given good input"""
        self.assertTrue(type(search_song_details(token, "Resonance", "Home")) == type({}))


class parse_input_test(unittest.TestCase):
    """Test module to test parse input function in `spotufy.py`"""
    def test_valid_return(self):
        """Function should return a non-empty string when called"""
        self.assertTrue(type(parse_input("ABxcII29238JJb"))==str and None!=parse_input("ABxcII29238JJb"))


class get_artist_releases_test(unittest.TestCase):
    """Test module to test get artist releases function in `spotufy.py`"""
    def test_invalid_artist_input(self):
        """Function should return None when not given an artist dictionary item as returned by `searchArtist()`"""
        self.assertTrue(None==get_artist_releases(token, "Al Green"))
    def test_valid_input(self):
        """Function should return an array of release items if given valid input and artist has releases"""
        self.assertTrue(type(get_artist_releases(token, {"name": "Al Green", "id": "3dkbV4qihUeMsqN4vBGg93"}))==type([]))


class get_top_tracks_test(unittest.TestCase):
    """Test module to test search artists function in `spotufy.py"""
    def test_valid_return(self):
        """Function should return a non-empty list if given good input"""
        self.assertTrue([]!= get_top_tracks(token, "Elton John"))
    def test_empty_input(self):
        """Function should return None if given bad input (artist parameter empty)"""
        self.assertTrue(None==(get_top_tracks(token, "")))
    def test_invalid_input(self):
        """Function should return None if given bad input (artist not found, no tracks returned)"""
        self.assertTrue(None==get_top_tracks(token, "asnldnwkandajdnakjdnakjndwkjdnaknsdnjwjknad"))


class get_genius_lyrics_test(unittest.TestCase):
    """Test module to test get Genius lyrics function in 'spotufy.py'"""
    def test_valid_return(self):
        """Function should return a non-empty string for valid input"""
        result = get_genius_lyrics("Bob Marley", "Lively Up Yourself")
        self.assertTrue(isinstance(result, str) and result != "")
    def test_invalid_artist_input(self):
        """Should return None if invalid input artist received"""
        result = get_genius_lyrics({"a":"b"}, "Track")
        self.assertTrue(result is None)
    def test_invalid_track_input(self):
        """Should return None if invalid input track received"""
        result = get_genius_lyrics("Artist", 1235)
        self.assertTrue(result is None)
    def test_missing_track_input(self):
        result = get_genius_lyrics("Bob Marley", "")
        self.assertTrue(result is None)
    def test_missing_artist_input(self):
        result = get_genius_lyrics("", "Lively Up Yourself")
        self.assertTrue(result is None)


class get_related_artists_test(unittest.TestCase):
    """Test module to test get related artists function in 'spotufy.py'"""
    def test_valid_return(self):
        """Should return a nonempty list for valid input"""
        result = get_related_artists(token, '0TnOYISbd1XYRBk9myaseg')
        self.assertTrue(isinstance(result, list) and result is not None)
    def test_invalid_input(self):
        """Should return None for invalid input"""
        result = get_related_artists(token, 23423)
        self.assertTrue(result is None)


class get_user_recs_test(unittest.TestCase):
    """Test module to test get_user_recs function in 'spotufy.py'"""
    def test_valid_return(self):
        """Should return a nonempty list for valid input"""
        result = get_user_recs(token)
        self.assertTrue(isinstance(result, list) and result is not None)
    def test_invalid_input(self):
        """Should return None in the event of an invalid input token"""
        result = get_user_recs('asdf')
        self.assertTrue(result is None)


class get_track_recs_test(unittest.TestCase):
    """Test module to test get_track_recs function in 'spotufy.py'"""
    def test_valid_return(self):
        """Should return a nonempty list for valid input"""
        result = get_track_recs(token, 'Bend Down Low', 'Bob Marley')
        self.assertTrue(isinstance(result, list) and result is not None)
    def test_invalid_input_token(self):
        """Should return None in the event of an invalid input token"""
        result = get_track_recs('asdf', 'Rednecks', 'Randy Newman')
        self.assertTrue(result is None)

    def test_invalid_input_track(self):
        """Should return None in the event of an invalid input track"""
        result = get_track_recs(token, '', 'Josh Lowe')
        self.assertTrue(result is None)
    def test_invalid_input_artist(self):
        """Should return None in the event of an invalid input artist"""
        result = get_track_recs(token, 'DevOps', '')
        self.assertTrue(result is None)


class create_playlist_test(unittest.TestCase):
    """Test module to test create_playlist function in 'spotufy.py'"""
    def test_valid_return(self):
        """Should return playlist URL if playlist is created successfully"""
        result = create_playlist(token, 'Test23', [{"uri":"spotify:track:6rqhFgbbKwnb9MLmUQDhG6"}])
        self.assertTrue(isinstance(result, str))

    def test_invalid_input_artist(self):
        """Should return None given invalid input playlist name"""
        result = create_playlist(token, [], [{"uri":"spotify:track:6rqhFgbbKwnb9MLmUQDhG6"}])
        self.assertTrue(result is None)

    def test_invalid_input_tracks(self):
        """Should return None given invalid input tracks"""
        result = create_playlist(token, 'Bob Marley', '')
        self.assertTrue(result is None)

if __name__ == '__main__':
    unittest.main()
