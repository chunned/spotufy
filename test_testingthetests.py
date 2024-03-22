import unittest
from spotufy import *
from app import app
from unittest.mock import patch, MagicMock

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
        mock_response.text = '{"artists": {"total":5,"items":{{"name":None,"external_urls":{"spotify":None},"followers":{"total":1000},"popularity":None,"genres":"Rock","id":None,"uri":None,"images":[{"url":None}]}}}}'
        mock_request.return_value = mock_response

        self.assertTrue([]!=search_artists("token", "Al Green"))
    @patch('spotufy.search_artists')
    def test_invalid_return(self, mock_request):
        """Function should return None if given bad input (no matching artist from search)"""

        # Configure the mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"artists":{"total":0}}
        mock_response.text = '{"artists":{"total":0}}'
        mock_request.return_value = mock_response

        self.assertTrue(None==search_artists("token", "sdfouhxiuheiuwer"))


class search_song_details_test(unittest.TestCase):
    """Test module to test search song details function in `spotufy.py`"""
    def test_blank_input(self):
        """Function should return None if given empty input"""
        self.assertTrue(None==search_song_details("token", "", ""))
    @patch('spotufy.search_song_details')
    def test_no_match(self, mock_request):
        """Function should return None if there is no matching result from API"""

        # Configure the mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"tracks":{"items":[]}}
        mock_response.text = '{"tracks":{"items":[]}}'
        mock_request.return_value = mock_response

        self.assertTrue(None==search_song_details("token", "Banana Pop Bozo", "Frisbee Cube Clock"))
    @patch('spotufy.make_api_call')
    def test_valid_return(self, mock_request):
        """Function should return a dictionary of track information if given good input"""

        # Configure the mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
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
        mock_response.text = '{"tracks": {"items":[{"id":None,"name":None,"album":{"name":None, "artists":[{"name":None}], "release_date":None, "images":["",{"url":None}]},"duration_ms":100000,"external_urls":{"spotify":None}}]}}'
        mock_request.return_value = mock_response
        
        self.assertTrue(type(search_song_details("token", "Resonance", "Home")) == type({}))


class get_artist_releases_test(unittest.TestCase):
    """Test module to test get artist releases function in `spotufy.py`"""
    @patch('spotufy.make_api_call')
    def test_invalid_artist_input(self, mock_request):
        """Function should return None when not given an artist ID item as returned by `search_artists()`."""
        self.assertTrue(None==get_artist_releases("token", "Al Green"))
    @patch('spotufy.get_artist_releases')
    def test_artist_no_releases(self, mock_request):
        """Function should return None when an artist is returned that has no releases"""

        # Configure the mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"total":0}
        mock_response.text = '{"total":0}'
        mock_request.return_value = mock_response

        self.assertTrue(None==get_artist_releases("token", {"name": "Al Green", "id": "3dkbV4qihUeMsqN4vBGg93"}))
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
        
        self.assertTrue(type(get_artist_releases("token", {"name": "Al Green", "id": "3dkbV4qihUeMsqN4vBGg93"}))==type([]))


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


if __name__ == '__main__':
    unittest.main()