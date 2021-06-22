from lxml import html


class InvalidGoogleHtml(Exception):
    """Invalid Google HTML provided.

    This exception is raised when the parser fails to parse the provided HTML string. It then
    assumes that the provided HTML is not a valid Google Search HTML source.
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class GoogleHtmlParser:
    """Google HTML Parser.

    This class parses the raw HTML from Google Search and transforms it into a usable
    dictionary. You can use this class to parse both Google Search mobile and desktop
    HTML responses.

    Attributes:
        tree: Holds the document object element parsed through html.fromstring()
    """

    def __init__(self, html_str) -> None:
        """Create the document tree.

        Parses the provided HTML string using html.fromstring() and
        sets the parsed object in the tree attribute.

        Args:
            html_str: Google Search HTML source as a string.
        """
        self.tree = html.fromstring(html_str)

    def _clean(self, content) -> str:
        """Clean content.

        It takes a malformed string, cleans it, and returns the cleaned string.

        Args:
            content: The string to clean.

        Returns:
            The cleaned string is returned.
        """

        if content:
            # Deal unicode strings
            content = content.encode('ascii', 'ignore').decode('utf-8')

            # Strip whitespaces
            content = content.strip()

            # Convert multiple spaces to one
            content = ' '.join(content.split())

            return content
        return ''

    def _get_estimated_results(self) -> int:
        """Get estimated results.

        Get the estimated results count as an integer for the performed search. Estimated results
        are available only in the HTML that Google returns for the desktop user agents.

        Returns:
            An integer of the estimated results count parsed from the tag div with ID result-stats.

        Raises:
            InvalidGoogleHtml: The HTML does not seem to be a valid Google SERPs HTML.
        """
        try:
            estimated_str = self.tree.xpath(
                '//*[@id="result-stats"]/text()')[0]
            return int(estimated_str.split()[1].replace(',', ''))
        except (ValueError, IndexError) as e:
            raise InvalidGoogleHtml(
                'The provided string does not seem to be a valid Google Search (Desktop) HTML.')

    def _get_organic(self) -> list:
        """Get organic results.

        This method returns the list of organic results. The data returned by this method doesn't
        contain other search features like featured snippets, people also ask section etc.

        Returns:
            A list of organic Google Search results is returned.
        """
        organic = []
        for g in self.tree.xpath('//div[@class="g"]'):
            snippets = g.xpath('.//div/div/div[2]/div')
            snippet = None
            rich_snippet = None
            if len(snippets) == 1:
                snippet = snippets[0].text_content()
            elif len(snippets) > 1:
                if len(snippets[0].xpath('.//span')) <= 1:
                    snippet = snippets[0].text_content()
                    rich_snippet = snippets[1].text_content()
                else:
                    snippet = snippets[1].text_content()
                    rich_snippet = snippets[0].text_content()

            res = {
                'url': self._clean(g.xpath('.//@href[1]')[0]),
                'title': self._clean(g.xpath('.//h3/text()')[0]),
                'snippet': self._clean(snippet),
                'rich_snippet': self._clean(rich_snippet),
            }
            organic.append(res)
        return organic

    def _get_featured_snippet(self) -> dict:
        """Get the featured snippet if exists.

        Get the featured snippet (title, url) if it exists. If it doesn't exists,
        then None is returned.

        Returns:
            None or dict. If featured snippet is missing, None will be returned,
            otherwise a dict. i.e. {'title': 'Example site title', 'url': 'http://example.com'}
        """
        fs = None
        snipp_el = self.tree.xpath(
            '//div[contains(concat(" ", @class, " "), "kp-blk")]')
        if len(snipp_el) > 0:
            snipp_el = snipp_el[0]
            heading = snipp_el.xpath('.//h3/text()')
            url = snipp_el.xpath('.//a/@href')
            if len(heading) > 0 and len(url) > 0:
                fs = {
                    'title': heading[0],
                    'url': url[-1]
                }

        return fs

    def get_data(self) -> dict:
        """Get the final data.

        Get the data including organic search results, estimated results count, and other
        elements as a dict.

        Returns:
            A dict that contains all SERP data including estimated results count, organic
            results, and more.
        """
        return {
            'estimated_results': self._get_estimated_results(),
            'featured_snippet': self._get_featured_snippet(),
            'organic_results': self._get_organic()
        }
