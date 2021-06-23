from lxml import html


class GoogleHtmlParser:
    """Google HTML Parser.

    This class parses the raw HTML from Google Search and transforms it into a usable
    dictionary. You can use this class to parse both Google Search mobile and desktop
    HTML responses.

    Attributes:
        tree: Holds the document object element parsed through html.fromstring()
        user_agent: Holds the user agent used to retrieve the Google Search HTML.
    """

    def __init__(self, html_str, user_agent='desktop') -> None:
        """Create the document tree.

        Parses the provided HTML string using html.fromstring() and
        sets the parsed object in the tree attribute.

        Args:
            html_str: Google Search HTML source as a string.
            user_agent: User agent used to get the Google Search HTML. Can be either
                        mobile or desktop
        """
        self.tree = html.fromstring(html_str)
        if user_agent in ['mobile', 'desktop']:
            self.user_agent = user_agent
        else:
            self.user_agent = 'desktop'

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
    
    def _normalize_dict_key(self, content) -> str:
        """Takes a string and makes it a standard dict key.
        
        This takes a string, replaces spaces with underscores, forces the elements to
        lower case and returns the string. The returned string can be used a dict key.
        """
        
        # Replace spaces with underscores
        content = str(content).replace(' ', '_')
        
        # Remove colons
        content = content.replace(':', '')
        
        # Remove underscores from end and beginning
        content = content.lower().strip('_')
        
        return content

    def _get_estimated_results(self) -> int:
        """Get estimated results.

        Get the estimated results count as an integer for the performed search. Estimated results
        are available only in the HTML that Google returns for the desktop user agents.

        Returns:
            An integer of the estimated results count parsed from the tag div with ID result-stats.
        """
        estimated_results = 0
        estimated_el = self.tree.xpath(
            '//*[@id="result-stats"]/text()')
        if len(estimated_el) > 0:
            estimated_results = int(
                estimated_el[0].split()[1].replace(',', ''))
        return estimated_results

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
                if len(snippets[1].xpath('.//g-review-stars')) > 0:
                    rich_snippet = snippets[1].text_content()
                    snippet = snippets[0].text_content()
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

        Get the featured snippet (title, url) if it exists. If it doesn't exist,
        then None is returned.

        Returns:
           any: A dict if featured snippet is found and None otherwise. i.e.::

                {
                    'title': 'Example site title',
                    'url': 'http://example.com'
                }
                
        """
        fs = None
        snipp_el = self.tree.xpath(
            '//div[contains(concat(" ", @class, " "), "kp-blk")]')
        if len(snipp_el) > 0:
            snipp_el = snipp_el[0]
            heading = snipp_el.xpath('.//h3/text()')
            url = snipp_el.xpath('.//a/@href')
            if all([len(item) > 0 for item in [heading, url]]):
                fs = {
                    'title': heading[0],
                    'url': url[-1]
                }

        return fs
    
    def _get_knowledge_card(self) -> dict:
        """Gets the knowledge card data if exists.
        
        For some search queries, for example search queries against bigger brands, and celebs, Google
        returns a knowledge card. It contains detailed information about the searched entituy. Generally,
        Google sources this data from Wikipedia as well as it uses its own database. If this card exists,
        this methods returns a dictionary, otherwise returns None.
        
        Returns:
            A dictionary if knowledge card exists, or None if it doesn't exist.
        """
        kc_el = self.tree.xpath('//div[contains(concat(" ", @class, " "), "kp-wholepage")]')
        if len(kc_el):
            kc_el = kc_el[0]
            more_info = []
            for el in kc_el.xpath('.//div[contains(@data-attrid, ":/")]'):
                el_parts = el.xpath('.//span')
                if len(el_parts) == 2:
                    more_info.append({
                        self._normalize_dict_key(el_parts[0].text_content()): el_parts[1].text_content()
                    })
                else:
                    heading = el.xpath('.//div[@role="heading"]')
                    if len(heading) > 0:
                        heading_anchor = heading[0].xpath('.//a')
                        if len(heading_anchor) > 0:
                            dict_key = self._normalize_dict_key(heading_anchor[0].text_content())
                            
                            dict_items = []
                            for item_div in el.xpath('.//div[@role="list"]'):
                                
                                # Get list items
                                for item in item_div.xpath('.//div[@role="heading"]'):
                                    if len(item):
                                        dict_items.append({
                                            'title': item.xpath('.//div[@class="title"]')[0].text_content(),
                                            'subtitle': item.xpath('.//div')[1].text_content()
                                        })
                        
                            if dict_key == 'people_also_search_for':
                                for pasf in el.xpath('.//div[@data-reltype="sideways"]'):
                                    dict_items.append(pasf.text_content())
                                
                            
                            more_info.append({
                                dict_key: dict_items
                            })
            
            return {
                'title': kc_el.xpath('.//h2/span')[0].text_content(),
                'subtitle': kc_el.xpath('.//div[contains(@data-attrid, "subtitle")]')[0].text_content(),
                'description': kc_el.xpath('.//div[@class="kno-rdesc"]/span')[0].text_content(),
                'more_info': more_info
            }
        
        return None

    def get_data(self) -> dict:
        """Get the final data.

        Get the data including organic search results, estimated results count, and other
        elements as a dict.

        Returns:
            A dict that contains all SERP data including estimated results count, organic
            results, and more.
        """
        data = {}
        if self.user_agent == 'desktop':
            data = {
                'estimated_results': self._get_estimated_results(),
                'featured_snippet': self._get_featured_snippet(),
                'organic_results': self._get_organic()
            }

        return data