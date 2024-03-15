import unittest
from spotufy import *

token = request_api_token()

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
        self.assertTrue(type(get_artist_releases(token, search_artists(token, "Al Green")))==type([]))

class get_top_tracks_test(unittest.TestCase):
    '''Test module to test search artists function in `main.py'''
    def test_valid_return(self):
        '''Function should return a non-empty list if given good input'''
        self.assertTrue([]!= get_top_tracks(token, "Elton John"))
    def test_empty_input(self):
        '''Function should return None if given bad input (artist parameter empty)'''
        self.assertTrue(None==(get_top_tracks(token, "")))
    def test_invalid_input(self):
        '''Function should return None if given bad input (artist not found, no tracks returned)'''
        self.assertTrue(None==get_top_tracks(token, "asnldnwkandajdnakjdnakjndwkjdnaknsdnjwjknad"))

# # Unit test template
# class name_test(unittest.TestCase):
#     '''Test module to test __ function in `spotufy.py`'''
#     def test_name(self):
#         ''''''
#         self.assertTrue()

if __name__ == '__main__':
        unittest.main()