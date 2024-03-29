import unittest
import json

from htmlparsers.google_search import GoogleHtmlParser
import requests


class TestGoogleHtmlParser(unittest.TestCase):
    """Test Google HTML Parser.

    This test case tests the GoogleHtmlParser class to ensure that it works as expected.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """Setup test resources.

        Setup the resources that we need to rely on in order to perform the tests.
        """
        cls.client = requests.session()
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        }
        keyword = 'data science'
        res = cls.client.get(
            f'https://www.google.com/search?q={keyword}&num=100', headers=headers)
        cls.parser = GoogleHtmlParser(html_str=res.text)

    @classmethod
    def tearDownClass(cls) -> None:
        """Close the client.

        Close the requests client as well as store the SERPs data as JSON to a file.
        """
        cls.client.close()
        
        data = cls.parser.get_data()
        with open('./data.json', 'w') as f:
            f.write(json.dumps(data))

    def test__get_organic(self) -> None:
        """Test organic results.

        Test organic results and ensure that the results are parsed correctly.
        """
        results = self.parser._get_organic()

        # Ensure that the data is a list
        self.assertEqual(type(results), list)

        # Confirm that the data has results
        self.assertGreater(len(results), 1)

    def test_results_has_url(self) -> None:
        """Test URL.

        Test that the result dict has the URL value set.
        """
        results = self.parser._get_organic()
        for result in results:
            self.assertNotEqual(result.get('url'), None)

    def test_results_has_title(self) -> None:
        """Test title.

        Ensure that the result dict has the title value set.
        """
        results = self.parser._get_organic()
        for result in results:
            self.assertNotEqual(result.get('title'), None)

    def test_results_has_snippet(self) -> None:
        """Test meta description snippet.

        Ensure that the result dict has the snippet value set.
        """
        results = self.parser._get_organic()
        for result in results:
            self.assertNotEqual(result.get('snippet'), None)

    def test__get_estimated_results(self) -> None:
        """Test estimated results.

        Ensure that we get the estimated results count from Google as an integer.
        """
        estimated_results = self.parser._get_estimated_results()
        self.assertEqual(type(estimated_results), int)

    def test_get_data(self) -> None:
        """Test final data.

        Ensure that we get the final data in form of a dictionary.
        """
        final_data = self.parser.get_data()
        self.assertEqual(type(final_data), dict)

    def test_featured_snippet(self) -> None:
        """Test featured snippet.

        Test either featured snippet was found or not. It should only be a dict
        or None.
        """
        fs = self.parser._get_featured_snippet()
        self.assertTrue(type(fs) in [None, dict])
    
    def test__get_knowledge_card(self) -> None:
        """Test knowledge card data.
        
        Test knowledge card data retrieval method to ensure that it works
        as expected.
        """
        kc = self.parser._get_knowledge_card()
        self.assertTrue(type(kc) in [None, dict])
    
    def test__get_scrolling_sections(self) -> None:
        """Test scrolling widgets.
        
        Test scrolling widgets data retrieval method to ensure that it works
        as expected.
        """
        sw = self.parser._get_scrolling_sections()
        self.assertEqual(type(sw), list)
        
