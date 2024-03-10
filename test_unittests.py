import unittest
from main import *

token = requestApiToken()

class request_api_token_test(unittest.TestCase):
    '''Test module to test request API token function in `main.py`'''
    def test_token_received(self):
        '''API token string should be returned and not be None'''
        self.assertTrue(None!=requestApiToken())

class search_artists_test(unittest.TestCase):
    '''Test module to test search artists function in `main.py'''
    def test_valid_return(self):
        '''Function should return a non-empty list if given good input'''
        self.assertTrue([]!=searchArtists(token, "Al Green"))
    def test_invalid_return(self):
        '''Function should return None if given bad input (no matching artist from search)'''
        self.assertTrue(None==searchArtists(token, "sdfouhxiuheiuwer"))








# Unit test template
class name_test(unittest.TestCase):
    '''Test module to test __ function in `main.py`'''
    def test_name(self):
        ''''''
        self.assertTrue()

if __name__ == '__main__':
        unittest.main()