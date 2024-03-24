import unittest
import requests
import werkzeug.wrappers.response

import spotufy
from unittest.mock import patch

class make_api_call_test(unittest.TestCase):
    """Test module to test API call function in `spotufy.py`"""

    @patch('spotufy.requests.request')
    def test_valid_return(self, mock_request):
        """Function should return a JSON object if given valid input"""
        response_object = requests.Response()
        # Override requests.Response().json() method using a lambda function
        response_object.json = lambda: {"name": "Mock Track"}
        response_object._content = b'{"name": "Mock Track"}'
        response_object.status_code = 200
        mock_request.return_value = response_object
        url = "https://api.spotify.com/v1/tracks/11dFghVXANMlKmJXsNCbNl"
        headers = {"Authorization": f"Bearer abcdefg"}
        response = spotufy.make_api_call(url, "GET", headers)
        self.assertIsInstance(response, dict)

    @patch('spotufy.requests.request', side_effect=requests.exceptions.HTTPError(401))
    def test_HTTP_error_return(self, mock_request):
        """Function should return None if an HTTP status code is raised"""
        # Invalid url, should raise a 401 error and return None
        url = "https://api."

        headers = {"Authorization": f"Bearer wefoijweoijsxoijwed"}
        response = spotufy.make_api_call(url, "GET", headers)
        self.assertTrue(response is None)


class request_api_token_test(unittest.TestCase):
    """Test module to test request API token function in `spotufy.py`"""
    @patch('spotufy.dotenv.dotenv_values')
    def test_token_received(self, secrets):
        secrets.return_value = {"CLIENT_ID": "1", "CALLBACK_URL": "http://"}
        """Redirect object to authentication URL should be returned"""
        response = spotufy.request_api_token()
        self.assertIsInstance(response, werkzeug.wrappers.response.Response)
        self.assertTrue(response.status_code == 302)


class parse_input_test(unittest.TestCase):
    """Test module to test parse input function in `spotufy.py`"""
    def test_valid_return(self):
        """Function should return a non-empty string when called"""
        response = spotufy.parse_input("ABxcII29238JJb")
        self.assertIsInstance(response, str)



# class create_playlist_test(unittest.TestCase):
#     """Test module to test create_playlist function in 'spotufy.py'"""
#     def test_valid_return(self):
#         """Should return playlist URL if playlist is created successfully"""
#         result = create_playlist(token, 'Test23', [{"uri":"spotify:track:6rqhFgbbKwnb9MLmUQDhG6"}])
#         self.assertTrue(isinstance(result, str))

#     def test_invalid_input_artist(self):
#         """Should return None given invalid input playlist name"""
#         result = create_playlist(token, [], [{"uri":"spotify:track:6rqhFgbbKwnb9MLmUQDhG6"}])
#         self.assertTrue(result is None)

#     def test_invalid_input_tracks(self):
#         """Should return None given invalid input tracks"""
#         result = create_playlist(token, 'Bob Marley', '')
#         self.assertTrue(result is None)


@patch('spotufy.make_api_call')
class search_artists_test(unittest.TestCase):
    """Test module to test search artists function in `spotufy.py`"""

    def test_valid_return(self, artists_response):
        """Function should return a non-empty list if given good input"""
        artists_response.return_value = {
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
        response = spotufy.search_artists("token", "Al Green")
        self.assertIsInstance(response, list)
        self.assertTrue(len(response) > 0)

    def test_invalid_return(self, artists_response):
        """Function should return None if given bad input (no matching artist from search)"""
        artists_response.return_value = {"artists":{"total":0}}
        response = spotufy.search_artists("token", "sdfouhxiuheiuwer")
        self.assertTrue(response is None)


@patch('spotufy.make_api_call')
class get_top_tracks_test(unittest.TestCase):
    """Test module to test search artists function in `spotufy.py"""

    def test_valid_return(self, api_response):
        """Function should return a non-empty list if given good input"""
        artist_response = {
            "artists":{
                "total":1,
                "items":[{
                    "name":None,
                    "external_urls":{"spotify":None},
                    "followers":{"total":1000},
                    "popularity":None,
                    "genres":"Rock",
                    "id":b"1234",
                    "uri":None,
                    "images":[{"url":None}]
                    }]
                }
            }
        tracks_response = {
                "tracks": [{
                    "name": None,
                    "album": {"name": None, "artists": [{"name": None}], "release_date": None,"images": ["", {"url": None}]},
                    "external_urls": {"spotify": None},
                    "popularity": None,
                    "uri": None,
                }]
        }
        api_response.side_effect = [artist_response, tracks_response]
        response = spotufy.get_top_tracks("token", "Elton John")
        self.assertIsInstance(response, list)
        self.assertTrue(len(response) > 0)

    def test_empty_input(self, api_response):
        """Function should return None if given bad input (artist parameter empty)"""
        # make_api_call returns None because of 400 error
        api_response.return_value = None 
        response = spotufy.get_top_tracks("token", "")
        self.assertTrue(response is None)

    def test_invalid_input(self, artists_response):
        """Function should return None if given bad input (artist not found, no tracks returned)"""        
        artists_response.return_value = {"artists":{"total":0}}
        response = spotufy.get_top_tracks("token", "asnldnwkandajdnak")
        self.assertTrue(response is None)


@patch('spotufy.make_api_call')
class search_song_details_test(unittest.TestCase):
    """Test module to test search song details function in `spotufy.py`"""

    def test_blank_input(self, song_response):
        """Function should return None if given empty input"""
        response = spotufy.search_song_details("token", "", "")
        self.assertTrue(response is None)

    def test_no_match(self, song_response):
        """Function should return None if there is no matching result from API"""
        song_response.return_value = {"tracks":{"items":[]}}
        response = spotufy.search_song_details("token", "Banana Pop Bozo", "Frisbee Cube Clock")
        self.assertTrue(response is None)

    def test_valid_return(self, song_response):
        """Function should return a dictionary of track information if given good input"""
        song_response.return_value = {
            "tracks": {
                "items":[{
                    "id":None,
                    "name":None,
                    "album":{"name":None, "artists":[{"name":None}], "release_date":None, "images":["",{"url":None}]},
                    "duration_ms":100000,
                    "external_urls":{"spotify":None}
                    }]
            }
        }
        response = spotufy.search_song_details("token", "Resonance", "Home")
        self.assertIsInstance(response, dict)
        self.assertTrue(len(response) > 0)


@patch('spotufy.make_api_call')
class get_track_recs_test(unittest.TestCase):
    """Test module to test get_track_recs function in `spotufy.py`"""

    def test_valid_return(self, recommended_tracks):
        """Should return a nonempty list for valid input"""
        track_dict = {"tracks":{"items":[{"id":"1234"}]}}
        recommended_tracks_dict = {
                "tracks": [{
                    "id":None,
                    "name": None,
                    "album": {"name": None, "artists": [{"name": None}], "images": [{"url": None}]},
                    "artists":[{"name":None}],
                    "external_urls": {"spotify": None},
                    "popularity": None,
                    "uri": None,
                }]
            }
        recommended_tracks.side_effect = [track_dict, recommended_tracks_dict]
        result = spotufy.get_track_recs("token", 'Bend Down Low', 'Bob Marley')
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)


    def test_invalid_input_token(self, api_response):
        """Should return None in the event of an invalid input token"""
        # make_api_call returns none because of 401 error
        api_response.return_value = None 
        result = spotufy.get_track_recs('asdf', 'Rednecks', 'Randy Newman')
        self.assertTrue(result is None)

    def test_invalid_input_track(self, api_response):
        """Should return None in the event of an invalid input track"""
        # make_api_call returns none because of 400 error
        api_response.return_value = None 
        result = spotufy.get_track_recs("token", '', 'Josh Lowe')
        self.assertTrue(result is None)

    def test_invalid_input_artist(self, api_response):
        """Should return None in the event of an invalid input artist"""
        # make_api_call returns none because of 400 error
        api_response.return_value = None 
        result = spotufy.get_track_recs("token", 'DevOps', '')
        self.assertTrue(result is None)


@patch('spotufy.make_api_call')
class get_user_recs_test(unittest.TestCase):
    """Test module to test get_user_recs function in 'spotufy.py'"""

    def test_valid_return(self, recommended_tracks):
        """Should return a nonempty list for valid input"""
        listened_tracks_dict = {"total":5,"items":[{"id":"1234"},{"id":"1234"},{"id":"1234"},{"id":"1234"},{"id":"1234"}]}
        recommended_tracks_dict = {
                "tracks": [{
                    "id":None,
                    "name": None,
                    "album": {"name": None, "artists": [{"name": None}], "images": [{"url": None}]},
                    "artists":[{"name":None}],
                    "external_urls": {"spotify": None},
                    "popularity": None,
                    "uri": None,
                }]
            }
        recommended_tracks.side_effect = [listened_tracks_dict, recommended_tracks_dict]
        result = spotufy.get_user_recs("token")
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)

    def test_invalid_input(self, api_response):
        """Should return None in the event of an invalid input token"""
        # make_api_call returns none because of 401 error
        api_response.return_value = None 
        result = spotufy.get_user_recs('asdf')
        self.assertTrue(result is None)


@patch('spotufy.make_api_call')
class get_related_artists_test(unittest.TestCase):
    """Test module to test get related artists function in `spotufy.py"""

    def test_valid_return(self, artists_response):
        """Should return a list given valid input"""
        artists_response.return_value = {"artists": [{"name": "Josh Lowe"}]}
        with patch('spotufy.search_artists') as search_artists:
            search_artists.return_value = "artist result"
            response = spotufy.get_related_artists('token', 'artist')
            self.assertIsInstance(response, list)
            self.assertTrue(len(response) > 0)


    def test_no_response(self, api_response):
        """Should return None if no response obtained"""
        api_response.return_value = None
        response = spotufy.get_related_artists('token', 'artist')
        self.assertTrue(response is None)

    def test_no_artists_found(self, artist_response):
        """Should return None if no matching artists found"""
        artist_response.return_value = {"artists": []}
        response = spotufy.get_related_artists('token', 'artist')
        self.assertTrue(response is None)


class get_genius_lyrics_test(unittest.TestCase):
    """Test module to test get Genius lyrics function in `spotufy.py"""

    @patch('spotufy.lyricsgenius.Genius.search_song')
    def test_valid_return(self, genius_response):
        """Should return a string given valid input; should also remove the first line of the string"""
        with patch('spotufy.dotenv.dotenv_values') as dotenv:
            dotenv.return_value = {"GENIUS_TOKEN": "1234"}
            genius_response.return_value.lyrics = "Lorem\nipsum\ndolor"
            response = spotufy.get_genius_lyrics('Dion', 'Only You Know')
            self.assertIsInstance(response, str)
            self.assertTrue(response == "ipsum\ndolor")

    def test_invalid_artist_type(self):
        """Should return None if given invalid input artist type"""
        with patch('spotufy.dotenv.dotenv_values') as dotenv:
            dotenv.return_value = {"GENIUS_TOKEN": "1234"}
            response = spotufy.get_genius_lyrics(1, "Song")
            self.assertTrue(response is None)

    def test_missing_artist(self):
        """Should return None if artist is missing"""
        with patch('spotufy.dotenv.dotenv_values') as dotenv:
            dotenv.return_value = {"GENIUS_TOKEN": "1234"}
            response = spotufy.get_genius_lyrics('', 'Song')
            self.assertTrue(response is None)

    def test_missing_song(self):
        """Should return None if song is missing"""
        with patch('spotufy.dotenv.dotenv_values') as dotenv:
            dotenv.return_value = {"GENIUS_TOKEN": "1234"}
            response = spotufy.get_genius_lyrics('Josh Lowe', '')
            self.assertTrue(response is None)

    def test_invalid_song_type(self):
        """Should return None if given invalid input song type"""
        with patch('spotufy.dotenv.dotenv_values') as dotenv:
            dotenv.return_value = {"GENIUS_TOKEN": "1234"}
            response = spotufy.get_genius_lyrics("Me", 1)
            self.assertTrue(response is None)


@patch('spotufy.make_api_call')
class get_artist_releases_test(unittest.TestCase):
    """Test module to test get artist releases function in `spotufy.py`"""

    def test_invalid_artist_input(self, releases_response):
        """Function should return None when not given an artist ID item as returned by `search_artists()`"""
        response = spotufy.get_artist_releases("token", "Al Green")
        self.assertTrue(response is None)

    def test_artist_no_releases(self, releases_response):
        """Function should return None when an artist is returned that has no releases"""
        releases_response.return_value = {"total":0}
        response = spotufy.get_artist_releases("token", {"name": "Al Green", "id": "3dkbV4qihUeMsqN4vBGg93"})
        self.assertTrue(response is None)

    def test_valid_input(self, releases_response):
        """Function should return an array of release items if given valid input and artist has releases"""
        releases_response.return_value = {
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
        response = spotufy.get_artist_releases("token", {"name": "Al Green", "id": "3dkbV4qihUeMsqN4vBGg93"})
        self.assertIsInstance(response, list)
        self.assertTrue(len(response) > 0)


if __name__ == '__main__':
    unittest.main()
