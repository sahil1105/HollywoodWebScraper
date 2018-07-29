from flask import Flask, jsonify, request,abort, make_response
from venv.DataAnalysis import extract_from_json
from venv.Graph import make_graph, Actor, Movie
import json
from venv.WebAPI import *
import unittest


class WebAPITests(unittest.TestCase):
    """
    Test Suite for the Movie-Actor Information API. Set (50,50) actors and movies to
    parse from the JSON.
    @author sahil1105
    """

    def setUp(self):
        """
        Setup the context and activate the API
        :return: self
        """
        self.app = app.test_client()

    def test_options(self):
        """
        Test the OPTIONS functionality
        :return: self
        """
        rv = self.app.options('/')  # Make the request
        # Following should be the response
        assert b'"Allow: GET, PUT, POST, DELETE, OPTIONS\\nTwo sub-APIs: \'movies\' and \'actors\'"\n' in rv.data
        self.assertEqual(rv.status_code, 200)

    def test_get_index(self):
        """
        Check the API Homepage functionality
        :return: self
        """
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 200)
        assert b'"Welcome to the Hollywood Database."' in rv.data  # Should be exactly this

    def test_actor_get_request_or(self):
        """
        Check the GET functionality for the custom OR query syntax (Movies API)
        :return: self
        """
        # Get Bruce Willis' and actors of age 62's information
        rv = self.app.get('/actors/name=Bruce_Willis|age=62')
        self.assertEqual(rv.status_code, 200)
        rv_json = json.loads(rv.data, encoding=bytes)
        # Ensure the data is correct
        assert b'"Bruce Willis"' in rv.data
        assert b'"Kathleen Quinlan"' in rv.data
        assert b'"The Jackal"' in rv.data
        assert len(rv_json) == 2
        assert rv_json[0]['age'] == 61
        # Ensure mis-formed queries are flagged
        rv = self.app.get('actors/name=Vruce_Willis|age=65')
        self.assertEqual(rv.status_code, 400)

    def test_movie_get_request_or(self):
        """
        Check the GET functionality for the custom OR query syntax (Actors API)
        :return: self
        """
        # Make a custom query
        rv = self.app.get('/movies/year=1982|box_office=39')
        self.assertEqual(rv.status_code, 200)
        rv_json = json.loads(rv.data, encoding=bytes)
        # print(json.dumps(rv_json, indent=4))
        # Ensure that the data holds up
        assert len(rv_json) == 2
        assert (rv_json[0]['year_released'] == 1982) or (rv_json[0]['gross_value'] == 39)
        assert (rv_json[1]['year_released'] == 1982) or (rv_json[1]['gross_value'] == 39)

    def test_actor_get_request(self):
        """
        Test GET functionality for Actors API
        :return: self
        """
        # Get Bruce Willis' information
        rv = self.app.get('/actors/Bruce_Willis')
        assert rv.status_code == 200  # Ensure the status code is correct
        rv_json = json.loads(rv.data, encoding=bytes)
        # print(json.dumps(rv_json, indent=4))
        assert rv_json['name'] == 'Bruce Willis'
        assert rv_json['age'] == 61
        # Ensure mis-formed queries are flagged
        rv = self.app.get('/actors/Jason_Sttatham')
        assert rv.status_code == 400

    def test_movie_get_request(self):
        """
        Test GET functionality on Movies API.
        :return: self
        """
        # Get info for the movie The Verdict
        rv = self.app.get('/movies/The_Verdict')
        assert rv.status_code == 200
        rv_json = json.loads(rv.data, encoding=bytes)
        # print(json.dumps(rv_json, indent=4))
        # Ensure the information is correct
        assert rv_json['name'] == "The Verdict"
        assert rv_json['year_released'] == 1982

        # Try to get a movie not in the database
        rv = self.app.get('/movies/The_Hangover')
        assert rv.status_code == 400
        rv_json = json.loads(rv.data, encoding=bytes)
        assert "Couldn't find" in rv_json

    def test_actor_get_request_and(self):
        """
        Test GET functionality with attribute matching syntax (Actors API)
        :return: self
        """
        # Make A request
        rv = self.app.get('/actors/?name=James_Whitmore&age=87')
        assert rv.status_code == 200
        rv_json = json.loads(rv.data, encoding=bytes)
        # print(json.dumps(rv_json, indent=4))
        # Check that the response holds up
        assert rv_json[0]['name'] == "James Whitmore" and rv_json[0]['age'] == 87

        # Make a request with no valid matches
        rv = self.app.get('actors/?age=54&total_gross=0')
        assert rv.status_code == 400

    def test_movie_get_request_and(self):
        """
        Test GET functionality with attribute matching syntax (Movies API)
        :return: self
        """
        # Make a request
        rv = self.app.get('/movies/?year=1994')
        assert rv.status_code == 200
        rv_json = json.loads(rv.data, encoding=bytes)
        # Ensure the data holds up for each object
        for movie in rv_json:
            assert movie['year_released'] == 1994

        # Ensure mis-informed queries are flagged
        rv = self.app.get('/movies/?year=1994&name=Northh')
        assert rv.status_code == 400
        rv_json = json.loads(rv.data, encoding=bytes)
        assert rv_json == []

    def test_actor_put_request(self):
        """
        Test PUT functionality of the Actors API
        :return: self
        """
        # Make an update request
        headers = {'content-type': 'application/json'}
        rv = self.app.put('/actors/Bruce_Willis', data=json.dumps({'age': 65}), headers=headers)
        assert rv.status_code == 201

        # Ensure the changes were made
        rv = self.app.get('/actors/Bruce_Willis')
        rv_json = json.loads(rv.data, encoding=bytes)
        assert rv_json['age'] == 65

        # Ensure mis-formed queries are flagged.
        rv = self.app.put('/actors/Jason_Sttatham', data=json.dumps({'age': 65}), headers=headers)
        assert rv.status_code == 400

    def test_movie_put_request(self):
        """
        Test PUT functionality of the Movies API
        :return: self
        """
        # Make an update request
        headers = {'content-type': 'application/json'}
        rv = self.app.put('/movies/Pulp_Fiction', data=json.dumps({'box_office': 234242,
                                                                   'actors': ['Test']}), headers=headers)
        assert rv.status_code == 201

        # Ensure the changes were made
        rv = self.app.get('/movies/Pulp_Fiction')
        rv_json = json.loads(rv.data, encoding=bytes)
        assert rv_json['gross_value'] == 234242 and rv_json['actors'] == ['Test']

        # Ensure that mis-formed requests are flagged
        rv = self.app.put('/movies/Pulp_Fiction', data=json.dumps({'age': 65}), headers=headers)
        assert rv.status_code == 400

        rv = self.app.put('/movies/Pulpy_Fiction', data=json.dumps({'year': 1965}), headers=headers)
        assert rv.status_code == 400

    def test_actor_post_request(self):
        """
        Test the POST functionality of the Actors API
        :return: self
        """
        # Make a POST request
        headers = {'content-type': 'application/json'}
        temp_dict = {'name': 'Mila Kunis', 'age': 31, 'movies': ['Friends with Benefits'], 'total_gross': 23424}
        rv = self.app.post('/actors/Mila_Kunis', data=json.dumps(temp_dict), headers=headers)
        assert rv.status_code == 201

        # Ensure the actor was added with the correct information
        rv = self.app.get('/actors/Mila_Kunis')
        rv_json = json.loads(rv.data, encoding=bytes)
        # print(json.dumps(rv_json, indent=4))
        assert rv_json == dict(name="Mila Kunis", age=31, movies_starred_in=['Friends with Benefits'],
                               gross_value=23424, edge_weights=[], edges=[])

    def test_movie_post_request(self):
        """
        Test the POST functionality of the Movies API
        :return: seld
        """
        # Make a POST request
        headers = {'content-type': 'application/json'}
        temp_dict = {'name': 'Prometheus', 'year': 2012, 'actors': ['Michael Fassbender'], 'box_office': 23424}
        rv = self.app.post('/movies/Prometheus', data=json.dumps(temp_dict), headers=headers)
        assert rv.status_code == 201

        # Ensure the movie was added with the correct information
        rv = self.app.get('/movies/Prometheus')
        rv_json = json.loads(rv.data, encoding=bytes)
        # print(json.dumps(rv_json, indent=4))
        assert rv_json == dict(name="Prometheus", year_released=2012, actors=['Michael Fassbender'],
                               gross_value=23424, edge_weights=[], edges=[])

        # Ensure that mis-formed requests are ignored
        temp_dict['shoulnt'] = 231
        rv = self.app.post('/movies/Prometheus', data=json.dumps(temp_dict), headers=headers)
        assert rv.status_code == 400

    def test_actor_delete_request(self):
        """
        Test DELETE functionality of the Actors API
        :return: self
        """
        # Make a GET request to ensure actor is originally there
        rv = self.app.get('/actors/David_Dukes')
        assert rv.status_code == 200
        # Make a DELETE request to delete it
        rv = self.app.delete('/actors/David_Dukes')
        assert rv.status_code == 201
        # Try to GET it to ensure it was deleted.
        rv = self.app.get('/actors/David_Dukes')
        assert rv.status_code == 400
        rv_json = json.loads(rv.data, encoding=bytes)
        assert "Couldn't find" in rv_json
        # Ensure that non-existent actors cannot be deleted.
        rv = self.app.delete('/actors/David_Dukes')
        assert rv.status_code == 400
        rv_json = json.loads(rv.data, encoding=bytes)
        assert "not in" in rv_json

    def test_movie_delete_request(self):
        """
        Test the DELETE functionality of the Movies API
        :return: self
        """
        # Make a GET request to ensure movie is originally there
        rv = self.app.get('/movies/Color_of_Night')
        assert rv.status_code == 200
        # Make a DELETE request to delete it
        rv = self.app.delete('/movies/Color_of_Night')
        assert rv.status_code == 201
        # Try to GET it to ensure it was deleted.
        rv = self.app.get('/movies/Color_of_Night')
        assert rv.status_code == 400
        rv_json = json.loads(rv.data, encoding=bytes)
        assert "Couldn't find" in rv_json
        # Ensure that non-existent movies cannot be deleted.
        rv = self.app.delete('/movies/Color_of_Night')
        assert rv.status_code == 400
        rv_json = json.loads(rv.data, encoding=bytes)
        assert "not in" in rv_json


if __name__ == '__main__':
    unittest.main()
