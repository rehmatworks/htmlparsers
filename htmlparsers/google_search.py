import json

from lxml import html
from lxml import etree


class GoogleHtmlParser:
    """Google HTML Parser

    This class parses the raw HTML from Google Search and transforms it to
    JSON. You can use this class to parse Google Search mobile and desktop
    HTML responses.
    """

    def __init__(self, html_str) -> None:
        """Set HTML content attribute

        This method takes the html argument and sets the tree attribute that we can access in other methods.
        """
        self.tree = html.fromstring(html_str)

    def _clean(self, content) -> str:
        """Clean content
        It takes a malformed string, cleans it, and returns the cleaned string.
        """
        if content:
            content = content.encode('ascii', 'ignore').decode('utf-8')
            content = content.strip()
            content = ' '.join(content.split())
            return content
        return ''

    def _get_organic(self) -> list:
        """Get organic results
        This method returns the list of organic results. The data returned by this method doesn't contain
        other search features like featured snippets, people also ask section and others.
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
