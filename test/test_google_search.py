import unittest
from snippets.google_search import GoogleHtmlParser
import requests


class TestGoogleHtmlParser(unittest.TestCase):
    """Test Google HTML Parser

    This test case tests the GoogleHtmlParser class to ensure that it works as expected.
    """

    def setUp(self):
        """Setup Test Resources

        Setup the resources that we need to rely on in order to perform the tests.
        """
        self.client = requests.session()
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        }
        res = self.client.get(
            'https://www.google.com/search?q=data+science&num=100', headers=headers)
        self.parser = GoogleHtmlParser(html_str=res.text)

    def tearDown(self):
        """Destroy the Resources

        Destroy all the resources that we created in order to run our tests.
        """
        self.client.close()

    def test_organic_results(self):
        """Test Organic Results

        Test organic results and ensure that the results are parsed correctly.
        """
        results = self.parser._get_organic()

        # Ensure that the data is a list
        self.assertEqual(type(results), list)

        # Confirm that the data has results
        self.assertGreater(len(results), 1)

    def test_result_has_url(self):
        """Ensure URL

        Ensure that the result dict has the URL value set.
        """
        results = self.parser._get_organic()
        result = results[0]
        self.assertNotEqual(result.get('url'), None)

    def test_result_has_title(self):
        """Ensure Title

        Ensure that the result dict has the title value set.
        """
        results = self.parser._get_organic()
        result = results[0]
        self.assertNotEqual(result.get('title'), None)
    
    def test_result_has_snippet(self):
        """Ensure Snippet
        
        Ensure that the result dict has the snippet value set.
        """
        results = self.parser._get_organic()
        result = results[0]
        self.assertNotEqual(result.get('snippet'), None)
