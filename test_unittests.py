import unittest
import base64
from spotufy import *
from app import app
import webbrowser
from unittest.mock import patch, MagicMock

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
        "redirect_uri": "https://ontario-tech-nits.github.io/final-project-group-1/index.html"
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


class parse_input_test(unittest.TestCase):
    """Test module to test parse input function in `spotufy.py`"""
    def test_valid_return(self):
        """Function should return a non-empty string when called"""
        self.assertTrue(type(parse_input("ABxcII29238JJb"))==str and None!=parse_input("ABxcII29238JJb"))


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

class search_artists_test(unittest.TestCase):
    """Test module to test search artists function in `spotufy.py"""
    @patch('spotufy.requests.request')
    def test_valid_return(self, mock_request):
        """Function should return a non-empty list if given good input"""

        # Configure the mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "artists": {
                "total":5,
                "items":[
                    {"name":None,
                    "external_urls":{"spotify":None},
                    "followers":{"total":1000},
                    "popularity":None,
                    "genres":"Rock",
                    "id":None,
                    "uri":None,
                    "images":[{"url":None}]}
                ]
            }
        }
        mock_response.text = '{"artists": {"total":5,"items":{{"name":None,"external_urls":{"spotify":None},"followers":{"total":1000},"popularity":None,"genres":"Rock","id":None,"uri":None,"images":[{"url":None}]}}}}'
        mock_request.return_value = mock_response

        self.assertTrue([]!=search_artists("token", "Al Green"))
    @patch('spotufy.requests.request', side_effect=requests.exceptions.HTTPError(404))
    def test_invalid_return(self, mock_request):
        """Function should return None if given bad input (no matching artist from search)"""

        # Configure the mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "artists": {
                "total":5,
                "items":[
                    {"name":None,
                    "external_urls":{"spotify":None},
                    "followers":{"total":1000},
                    "popularity":None,
                    "genres":"Rock",
                    "id":None,
                    "uri":None,
                    "images":[{"url":None}]}
                ]
            }
        }
        mock_response.text = '{"artists": {"total":5,"items":{{"name":None,"external_urls":{"spotify":None},"followers":{"total":1000},"popularity":None,"genres":"Rock","id":None,"uri":None,"images":[{"url":None}]}}}}'
        mock_request.return_value = mock_response

        self.assertTrue(None==search_artists("token", "sdfouhxiuheiuwer"))


class get_top_tracks_test(unittest.TestCase):
    """Test module to test search artists function in `spotufy.py"""
    @patch('spotufy.search_artists')
    @patch('spotufy.get_top_tracks')
    def test_valid_return(self, mock_request_artist, mock_request_tracks):
        """Function should return a non-empty list if given good input"""

        # Configure the mock response for the search_artists function
        mock_response_artist = MagicMock()
        mock_response_artist.json.return_value = {
            "artists": {
                "total":5,
                "items":[{
                    "name":None,
                    "external_urls":{"spotify":None},
                    "followers":{"total":1000},
                    "popularity":None,
                    "genres":"Rock",
                    "id":None,
                    "uri":None,
                    "images":[{"url":None}]
                    }]
            }
        }
        mock_response_artist.text = '{"artists": {"total":5,"items":{{"name":None,"external_urls":{"spotify":None},"followers":{"total":1000},"popularity":None,"genres":"Rock","id":None,"uri":None,"images":[{"url":None}]}}}}'
        mock_request_artist.return_value = mock_response_artist

        # Configure the mock response for the get_top_tracks function
        mock_response_tracks = MagicMock()
        mock_response_tracks.json.return_value = {
            "tracks": [{
                "name":None,
                "album":{"name":None, "artists":[{"name":None}], "release_date":None, "images":["",{"url":None}]},
                "external_urls":{"spotify":None},
                "populartiy":None,
                "uri":None,
            }]
        }
        mock_response_tracks.text = '{"tracks": [{"name":None,"album":{"name":None, "artists":[{"name":None}], "release_date":None, "images":["",{"url":None}]},"external_urls":{"spotify":None},"populartiy":None,"uri":None,}]}'
        mock_request_tracks.return_value = mock_response_tracks

        self.assertTrue([]!=get_top_tracks("token", "Elton John"))
    @patch('spotufy.get_top_tracks', side_effect=requests.exceptions.HTTPError(400))
    def test_empty_input(self, mock_request):
        """Function should return None if given bad input (artist parameter empty)"""

        # Configure the mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"error":{"status":400,"message":"No search query"}}
        mock_response.text = '{"error":{"status":400,"message":"No search query"}}'
        mock_request.return_value = mock_response

        self.assertTrue(None==(get_top_tracks("token", "")))
    @patch('spotufy.get_top_tracks')
    def test_invalid_input(self, mock_request):
        """Function should return None if given bad input (artist not found, no tracks returned)"""
        
        # Configure the mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"artists":{"total":0}}
        mock_response.text = '{"artists":{"total":0}}'
        mock_request.return_value = mock_response
        
        self.assertTrue(None==get_top_tracks("token", "asnldnwkandajdnak"))

class search_song_details_test(unittest.TestCase):
    """Test module to test search song details function in `spotufy.py`"""
    def test_blank_input(self):
        """Function should return None if given empty input"""
        self.assertTrue(None==search_song_details("token", "", ""))
    
    @patch('spotufy.requests.request')
    def test_no_match(self, mock_request):
        """Function should return None if there is no matching result from API"""

        # Configure the mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"tracks":{"items":[]}}
        mock_response.text = '{"tracks":{"items":[]}}'
        mock_request.return_value = mock_response
        self.assertTrue(None==search_song_details("token", "Banana Pop Bozo", "Frisbee Cube Clock"))
    
    @patch('spotufy.requests.request')
    def test_valid_return(self, mock_request):
        """Function should return a dictionary of track information if given good input"""

        # Configure the mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "tracks": {
                "items":[
                    {"id":None,
                    "name":None,
                    "album":{"name":None, "artists":[{"name":None}], "release_date":None},
                    "duration_ms":100000,
                    "external_urls":{"spotify":None},
                    "images":None}
                ]
            }
        }
        mock_response.text = '{"tracks": {"items":[{"id":None,"name":None,"album":{"name":None, "artists":[{"name":None}], "release_date":None},"duration_ms":100000,"external_urls":{"spotify":None}}]}}'
        mock_request.return_value = mock_response
        self.assertTrue(type(search_song_details("token", "Resonance", "Home")) == type({}))


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


class get_artist_releases_test(unittest.TestCase):
    """Test module to test get artist releases function in `spotufy.py`"""
    @patch('spotufy.requests.request')
    def test_invalid_artist_input(self, mock_request):
        """Function should return None when not given an artist ID item as returned by `search_artists()`."""
        self.assertTrue(None==get_artist_releases("token", "Al Green"))
    @patch('spotufy.requests.request')
    def test_artist_no_releases(self, mock_request):
        """Function should return None when an artist is returned that has no releases"""

        # Configure the mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"total":0}
        mock_response.text = '{"total":0}'
        mock_request.return_value = mock_response

        self.assertTrue(None==get_artist_releases("token", {"name": "Al Green", "id": "3dkbV4qihUeMsqN4vBGg93"}))
    @patch('spotufy.requests.request')
    def test_valid_input(self, mock_request):
        """Function should return an array of release items if given valid input and artist has releases"""
        
        # Configure the mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total":1,
            "items": [{
                "album_group":None,
                "external_urls":{"spotify":None},
                "id":None,
                "artists":[None],
                "name":None,
                "release_date":None,
                "total_tracks":None,
                "images":[{"url":None}]
            }]
        }
        mock_response.text = '{"items": {{"album_group":None,"external_urls":{"spotify":None},"id":None,"artists":[None],"names":None,"release_date":None,"total_tracks":None}}}'
        mock_request.return_value = mock_response
        
        self.assertTrue(type(get_artist_releases("token", {"name": "Al Green", "id": "3dkbV4qihUeMsqN4vBGg93"}))==type([]))


if __name__ == '__main__':
    unittest.main()
