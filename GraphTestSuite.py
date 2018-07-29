import unittest
import WebScraper
import Graph


class TestGraphMethods(unittest.TestCase):
    """
    Unit Test Class to test implementation of the methods in Graph Module.
    @author sahil1105
    """
    def setUp(self):
        """
        Setup method for the rest of the tests
        :return: self
        """
        self.movies = WebScraper.retrieve_movies_from_json('test_movies.json')
        self.actors = WebScraper.retrieve_actors_from_json('test_actors.json')

    def test_make_graph(self):
        """
        Tests the implementation of the make_graph function.
        This in turn also checks the implementation of assign_weights_to_edges,
        make_edges_from_movies_actors, make_edges_from_actors_to_movies and
        calc_edge_weights.
        :return:
        """
        self.actors, self.movies = Graph.make_graph(self.actors, self.movies)  # Make the graph
        # Ensure the lengths are correct
        self.assertEqual(len(self.actors), 8)
        self.assertEqual(len(self.movies), 4)
        # Ensure the types of the object are right
        for k, v in self.actors.items():
            self.assertEqual(type(v), Graph.Actor)
        for k, v in self.movies.items():
            self.assertEqual(type(v), Graph.Movie)
        # Ensure that edges have been properly assigned
        self.assertEqual(self.actors['Morgan Freeman'].edges[0], self.movies['Brubaker'])
        self.assertEqual(self.movies['Brubaker'].edges[0], self.actors['Morgan Freeman'])
        # Ensure every edge has a counterpart in the other list
        for name, actor_node in self.actors.items():
            for edge in actor_node.edges:
                self.assertEqual(edge in list(self.movies.values()), True)
        for name, movie_node in self.movies.items():
            for edge in movie_node.edges:
                self.assertEqual(edge in list(self.actors.values()), True)
        # Check that edge weights on both nodes is the same
        self.assertEqual(self.actors['David Keith'].edge_weights[0], self.movies['Brubaker'].edge_weights[5])

    def test_get_movie_gross_value(self):
        """
        Tests the implementation of the query helper which finds the gross value of a given movie.
        :return: self
        """
        self.test_make_graph()  # Create the graph
        # Check that the values are correct
        self.assertAlmostEqual(Graph.get_movie_gross_value(self.movies, 'Marie (film)'), 2507995.0)
        self.assertAlmostEqual(Graph.get_movie_gross_value(self.movies, 'Brubaker'), 371217082.0)
        self.assertAlmostEqual(Graph.get_movie_gross_value(self.movies, 'Glory (1989 film)'), 26800000.0)
        # Check that output is -1 for MOVIES not in the graph
        self.assertEqual(Graph.get_movie_gross_value(self.movies, 'The Shawshank Redemption'), -1)

    def test_get_movies_starred_in(self):
        """
        Tests the implementation of the query helper which finds the MOVIES an actor has starred in.
        :return: self
        """
        self.test_make_graph()  # Create the graph
        # Check that the elements and length of lists is correct
        self.assertEqual(Graph.get_movies_starred_in(self.actors, 'Morgan Freeman')[5], 'Driving Miss Daisy')
        self.assertEqual(len(Graph.get_movies_starred_in(self.actors, 'Murray Hamilton')), 1)
        self.assertEqual(Graph.get_movies_starred_in(self.actors, 'Jeff Daniels')[57], 'The Martian')

    def test_get_starred_actors(self):
        """
        Tests the implementation of the query helper which finds the ACTORS that have starred in a given movie.
        :return: self
        """
        self.test_make_graph()  # Create the graph
        # Check the contents of a specific call
        self.assertEqual(Graph.get_starred_actors(self.movies, 'Marie (film)'), ['Sissy Spacek', 'Jeff Daniels',
                                                                                 'Keith Szarabajka', 'Morgan Freeman',
                                                                                 'Fred Thompson'])
        # Check that the lengths are correct
        self.assertEqual(len(Graph.get_starred_actors(self.movies, 'Brubaker')), 7)
        # Check that unlisted MOVIES return []
        self.assertEqual(Graph.get_starred_actors(self.actors, 'The Shawshank Redemption'), [])

    def test_n_highest_grossing_actors(self):
        """
        Tests the implementation of the query helper which finds the ACTORS that have the highest grossing values.
        :return: self
        """
        self.test_make_graph()  # Create the graph
        # Ensure the orderings are correct
        self.assertEqual(Graph.n_highest_grossing_actors(self.actors, 4), ['Morgan Freeman', 'Yaphet Kotto',
                                                                           'Jane Alexander', 'Robert Redford'])
        self.assertEqual(Graph.n_highest_grossing_actors(self.actors, 7), ['Morgan Freeman', 'Yaphet Kotto',
                                                                           'Jane Alexander', 'Robert Redford',
                                                                           'Murray Hamilton', 'David Keith',
                                                                           'Sissy Spacek'])
        # Ensure that it performs properly even when n > len(ACTORS)
        self.assertEqual(Graph.n_highest_grossing_actors(self.actors, 20), ['Morgan Freeman', 'Yaphet Kotto',
                                                                            'Jane Alexander', 'Robert Redford',
                                                                            'Murray Hamilton', 'David Keith',
                                                                            'Sissy Spacek', 'Jeff Daniels'])

    def test_n_oldest_actors(self):
        """
        Tests the implementation of the query helper which finds the n ACTORS that are the oldest.
        :return: self
        """
        self.test_make_graph()  # Create the graph
        # Ensure the orderings are correct
        self.assertEqual(Graph.n_oldest_actors(self.actors, 3), ['Murray Hamilton', 'Robert Redford', 'Morgan Freeman'])
        self.assertEqual(Graph.n_oldest_actors(self.actors, 2), ['Murray Hamilton', 'Robert Redford'])
        self.assertEqual(Graph.n_oldest_actors(self.actors, 20), ['Murray Hamilton', 'Robert Redford',
                                                                  'Morgan Freeman', 'Yaphet Kotto',
                                                                  'Jane Alexander', 'Sissy Spacek',
                                                                  'David Keith', 'Jeff Daniels'])
        # Ensure that it performs properly even when n > len(ACTORS)
        self.assertEqual(Graph.n_oldest_actors(self.actors, 7), ['Murray Hamilton', 'Robert Redford',
                                                                  'Morgan Freeman', 'Yaphet Kotto',
                                                                  'Jane Alexander', 'Sissy Spacek',
                                                                  'David Keith'])

    def test_get_movies_in_a_year(self):
        """
        Tests the implementation of the query helper which finds the MOVIES that were released in a certain year.
        :return: self
        """
        self.test_make_graph()  # Create the graph
        # Ensure that the correct MOVIES are enlisted
        self.assertEqual(Graph.get_movies_in_a_year(self.movies, 1989), ['Glory (1989 film)'])
        self.assertEqual(Graph.get_movies_in_a_year(self.movies, 1980), ['Brubaker'])
        self.assertEqual(Graph.get_movies_in_a_year(self.movies, 1985), ['Marie (film)',
                                                                         'That Was Then... This Is Now'])
        # Ensure that no MOVIES show up when none of the scraped MOVIES were released that year
        self.assertEqual(Graph.get_movies_in_a_year(self.movies, 1994), [])

    def test_get_actors_in_a_year(self):
        """
        Tests the implementation of the query helper which finds the ACTORS that starred in some movie released
        in a given year.
        :return: self
        """
        self.test_make_graph()  # Create the graph
        # Ensure that the correct ACTORS are enlisted
        self.assertEqual(set(Graph.get_actors_in_a_year(self.movies, 1989)),
                         {'Morgan Freeman', 'Denzel Washington', 'Cary Elwes', 'Matthew Broderick'})
        self.assertEqual(set(Graph.get_actors_in_a_year(self.movies, 1980)),
                         {'Yaphet Kotto', 'Robert Redford', 'Tim McIntire', 'Jane Alexander', 'Morgan Freeman',
                          'David Keith', 'Murray Hamilton'})
        self.assertEqual(set(Graph.get_actors_in_a_year(self.movies, 1985)),
                         {'Keith Szarabajka', 'Sissy Spacek', 'Kim Delaney', 'Jeff Daniels', 'Morgan Freeman',
                          'Jill Schoelen', 'Craig Sheffer', 'Larry Scott', 'Barbara Babcock', 'Fred Thompson'})
        # Ensure that no ACTORS show up when none of the scraped MOVIES were released that year
        self.assertEqual(set(Graph.get_actors_in_a_year(self.movies, 1994)), set([]))


if __name__ == '__main__':
    unittest.main()

