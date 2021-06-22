import unittest
from htmlparsers.google_search import GoogleHtmlParser, InvalidGoogleHtml
import requests


class TestGoogleHtmlParser(unittest.TestCase):
    """Test Google HTML Parser

    This test case tests the GoogleHtmlParser class to ensure that it works as expected.
    """

    def setUp(self) -> None:
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

    def tearDown(self) -> None:
        """Destroy the Resources

        Destroy all the resources that we created in order to run our tests.
        """
        self.client.close()

    def test__get_organic(self) -> None:
        """Test Organic Results

        Test organic results and ensure that the results are parsed correctly.
        """
        results = self.parser._get_organic()

        # Ensure that the data is a list
        self.assertEqual(type(results), list)

        # Confirm that the data has results
        self.assertGreater(len(results), 1)

    def test_results_has_url(self) -> None:
        """Ensure URL

        Test that the result dict has the URL value set.
        """
        results = self.parser._get_organic()
        for result in results:
            self.assertNotEqual(result.get('url'), None)

    def test_results_has_title(self) -> None:
        """Test Title

        Ensure that the result dict has the title value set.
        """
        results = self.parser._get_organic()
        for result in results:
            self.assertNotEqual(result.get('title'), None)
    
    def test_results_has_snippet(self) -> None:
        """Test Snippet
        
        Ensure that the result dict has the snippet value set.
        """
        results = self.parser._get_organic()
        for result in results:
            self.assertNotEqual(result.get('snippet'), None)
    
    def test__get_estimated_results(self) -> None:
        """Test Estimated Results
        
        Ensure that we get the estimated results count from Google as an integer.
        """
        estimated_results = self.parser._get_estimated_results()
        self.assertEqual(type(estimated_results), int)
    
    def test_get_data(self) -> None:
        """Test Final Data
        
        Ensure that we get the final data in form of a dictionary.
        """
        final_data = self.parser.get_data()
        self.assertEqual(type(final_data), dict)
    
    def test_invalid_google_html(self) -> None:
        """Test Invalid HTML
        
        Provide an invalid string as the HTML source and ensure that InvalidGoogleHtml exception is raised.
        """
        
        html_str = """
        <!DOCTYPE html>
        <html>
            <head>
                <title>Invalid HTML source</title>
            </head>
            <body>
                <p>This source does not contain any Google Search results.</p>
            </body>
        </html>
        """
        parser = GoogleHtmlParser(html_str)
        self.assertRaises(InvalidGoogleHtml, parser._get_estimated_results)
