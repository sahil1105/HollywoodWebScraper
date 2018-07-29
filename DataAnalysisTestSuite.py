import unittest
from venv.DataAnalysis import *
from venv.Graph import *


class TestDataAnalysis(unittest.TestCase):
    """
    Unit Tests for the Data Analysis
    @author sahil1105
    """

    def setUp(self):
        """
        Sets up the graph for the test cases.
        :return: self
        """
        self.actors, self.movies = extract_from_json('/Users/sahil1105/OneDrive/Spring 2018/CS 242/'
                                                     'svnRepo/Assignment2.1/venv/data.json')  # Get the data
        self.actors, self.movies = make_graph(self.actors, self.movies)  # Form the edges between the actors and movies

    def test_hub_actors(self):
        """
        Tests that the right hub actors are identified.
        :return: self
        """
        hub_actors = get_hub_actors(self.actors, 10)  # Get the top 10 hub actors
        assert hub_actors == ['Bruce Willis', 'Jack Warden', 'Faye Dunaway', 'Paul Newman',
                              'Brenda Vaccaro', 'Andie MacDowell', 'John Cusack',
                              'Steve Buscemi', 'Mickey Rourke', 'Nick Nolte']

    def test_get_average_gross_value_per_movie(self):
        """
        Tests the functionality of the get_average_gross_value_per_movie function.
        :return: self
        """
        hub_actors = get_hub_actors(self.actors, 10)  # Get the top 10 hub actors
        hub_actors = {actor_name: self.actors[actor_name] for actor_name in hub_actors}  # Convert to a dict
        self.assertAlmostEqual(get_average_gross_value_per_movie(hub_actors), 3204062.753093549)
        self.assertAlmostEqual(get_average_gross_value_per_movie(self.actors), 292982.2335557605)

    def test_plots(self):
        """
        Tests the functionality of the various plot functions. For these it just ensures
        that these do not raise any exceptions.
        :return:
        """
        hub_actors = get_hub_actors(self.actors, 10)  # Get the top 10 hub actors
        hub_actors = {actor_name: self.actors[actor_name] for actor_name in hub_actors}  # Convert to a dict
        plot_hub_actors(hub_actors, False)  # Plot the hub actors
        plot_age_grossing_scatter(self.actors, False)
        plot_age_num_movies_scatter(self.actors, False)
        plot_year_num_movies(self.movies, False)


if __name__ == '__main__':
    unittest.main()

