import unittest
import WebScraper
import Graph

class TestWebScraper(unittest.TestCase):
    """
    Unit Test class to test some of the predictable functionality of the WebScraper.
    @author sahil1105
    """

    def test_scrape_movie_page(self):
        """
        Tests that invalid links don't work but that they don't crash either.
        :return: self
        """
        # Test that invalid links don't work
        self.assertEqual(WebScraper.scrape_movie_page('Black Panther', "https://en.wikipedia.org/Blac_Panther"),
                         (None, {}))

    def test_scrape_actor_page(self):
        """
        Tests that invalid links don't work but that they don't crash either.
        :return: self
        """
        # Test that invalid links don't work
        self.assertEqual(WebScraper.scrape_actor_page('Gal Gadot', "https://en.wikipedia.org/Ga_Gadot"),
                         (None, {}))


if __name__ == '__main__':
    unittest.main()