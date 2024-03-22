import unittest
import requests
from unittest.mock import patch, MagicMock
import spotufy

"""
DONE:
- make_api_call
- search_artists
- search_song_details
- get_artist_releases
- get_top_tracks

TODO:
- create_playlist
- get_track_recs
- get_user_recs
- get_related_artists
- get_genius_lyrics
"""


class make_api_call_test(unittest.TestCase):
    """Test module to test API call function in `spotufy.py`"""
    @patch('spotufy.requests.request')
    def test_valid_return(self, mock_request):
        """Function should return a JSON object if given valid input"""

        # Configure the mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"name": "Mock Track"}
        mock_response.text = '{"name": "Mock Track"}'
        mock_response.raise_for_status.return_value = None

        mock_request.return_value = mock_response

        url = "https://api.spotify.com/v1/tracks/11dFghVXANMlKmJXsNCbNl"
        headers = {"Authorization": f"Bearer abcdefg"}
        response = spotufy.make_api_call(url, "GET", headers)

        self.assertTrue(type(response) == type({}))

    @patch('spotufy.requests.request', side_effect=requests.exceptions.HTTPError(401))
    def test_HTTP_error_return(self, mock_request):
        """Function should return None if an HTTP status code is raised"""


        # Invalid url, should raise a 401 error and return None
        url = "https://api."

        headers = {"Authorization": f"Bearer wefoijweoijsxoijwed"}
        response = spotufy.make_api_call(url, "GET", headers)
        self.assertTrue(None==response)


class search_artists_test(unittest.TestCase):
    """Test module to test search artists function in `spotufy.py`"""
    @patch('spotufy.make_api_call')
    def test_valid_return(self, mock_request):
        """Function should return a non-empty list if given good input"""

        # Configure the mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
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

        mock_request.return_value = mock_response

        self.assertTrue([]!=spotufy.search_artists("token", "Al Green"))
    @patch('spotufy.requests.request')
    def test_invalid_return(self, mock_request):
        """Function should return None if given bad input (no matching artist from search)"""

        # Configure the mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"artists":{"total":0}}
        mock_request.return_value = mock_response

        response = spotufy.search_artists("token", "sdfouhxiuheiuwer")

        self.assertTrue(None == response)


class search_song_details_test(unittest.TestCase):
    """Test module to test search song details function in `spotufy.py`"""
    def test_blank_input(self):
        """Function should return None if given empty input"""
        self.assertTrue(None==spotufy.search_song_details("token", "", ""))
    @patch('spotufy.make_api_call')
    def test_no_match(self, mock_request):
        """Function should return None if there is no matching result from API"""
        # Configure the mock response
        mock_request.return_value = {"tracks":{"items":[]}}

        response = spotufy.search_song_details("token", "Banana Pop Bozo", "Frisbee Cube Clock")
        self.assertTrue(None==response)
    @patch('spotufy.make_api_call')
    def test_valid_return(self, mock_request):
        """Function should return a dictionary of track information if given good input"""
        # Configure the mock response
        mock_request.return_value = {
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

        self.assertTrue(type(spotufy.search_song_details("token", "Resonance", "Home")) == type({}))


class get_artist_releases_test(unittest.TestCase):
    """Test module to test get artist releases function in `spotufy.py`"""
    def test_invalid_artist_input(self):
        """Function should return None when not given an artist ID item as returned by `search_artists()`."""
        self.assertTrue(None==spotufy.get_artist_releases("token", "Al Green"))

    @patch('spotufy.make_api_call')
    def test_artist_no_releases(self, mock_request):
        """Function should return None when an artist is returned that has no releases"""

        # Configure the mock response
        mock_request.return_value = {"total":0}

        self.assertTrue(None==spotufy.get_artist_releases("token", {"name": "Al Green", "id": "3dkbV4qihUeMsqN4vBGg93"}))
    @patch('spotufy.make_api_call')
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
        
        self.assertTrue(type(spotufy.get_artist_releases("token", {"name": "Al Green", "id": "3dkbV4qihUeMsqN4vBGg93"}))==type([]))


class get_top_tracks_test(unittest.TestCase):
    """Test module to test search artists function in `spotufy.py"""
    @patch('spotufy.search_artists')
    def test_valid_return(self, mock_request_artist):
        """Function should return a non-empty list if given good input"""

        # Configure the mock response for the search_artists function
        mock_request_artist.return_value = ['',{
                    "name":None,
                    "external_urls":{"spotify":None},
                    "followers":{"total":1000},
                    "popularity":None,
                    "genres":"Rock",
                    "id":b"1234",
                    "uri":None,
                    "images":[{"url":None}]
                    }]

        dic = {
                "tracks": [{
                    "name": None,
                    "album": {"name": None, "artists": [{"name": None}], "release_date": None,
                              "images": ["", {"url": None}]},
                    "external_urls": {"spotify": None},
                    "popularity": None,
                    "uri": None,
                }]
        }

        with patch('spotufy.make_api_call') as api_call_patch:
            api_call_patch.return_value = dic
            response = spotufy.get_top_tracks("token", "Elton John")
            self.assertTrue([]!=response)

    @patch('spotufy.requests.request', side_effect=requests.exceptions.HTTPError(400))
    def test_empty_input(self, mock_request):
        """Function should return None if given bad input (artist parameter empty)"""

        response = spotufy.get_top_tracks("token", "")
        self.assertTrue(None == response)
    @patch('spotufy.make_api_call')
    def test_invalid_input(self, mock_request):
        """Function should return None if given bad input (artist not found, no tracks returned)"""
        
        # Configure the mock response
        mock_request.return_value = {"artists":{"total":0}}
        
        self.assertTrue(None==spotufy.get_top_tracks("token", "asnldnwkandajdnak"))

# class create_playlist_test(unittest.TestCase):
#     """Test module to test create_playlist function in 'spotufy.py'"""
#     def test_valid_return(self):
#         """Should return playlist URL if playlist is created successfully"""
#         result = spotufy.create_playlist("token", 'Test23', [{"uri":"spotify:track:6rqhFgbbKwnb9MLmUQDhG6"}])
#         self.assertTrue(isinstance(result, str))

#     def test_invalid_input_artist(self):
#         """Should return None given invalid input playlist name"""
#         result = spotufy.create_playlist("token", [], [{"uri":"spotify:track:6rqhFgbbKwnb9MLmUQDhG6"}])
#         self.assertTrue(result is None)

#     def test_invalid_input_tracks(self):
#         """Should return None given invalid input tracks"""
#         result = spotufy.create_playlist("token", 'Bob Marley', '')
#         self.assertTrue(result is None)

if __name__ == '__main__':
    unittest.main()