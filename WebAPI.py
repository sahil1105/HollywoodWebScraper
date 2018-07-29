from flask import Flask, jsonify, request,abort, make_response
from venv.DataAnalysis import extract_from_json
from venv.Graph import make_graph, Actor, Movie

"""
Reference:
https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
https://stackoverflow.com/questions/405489/python-update-object-from-dictionary
"""

# Actors and Movies Dicts that serve as the database for the API
ACTORS, MOVIES = extract_from_json('data.json', 50, 50)

# Dictionaries to help convert JSON attribute values to GraphNode variable names
ACTOR_JSON_TO_NODE_DICT = {'name': 'name',
                            'age': 'age',
                            'total_gross': 'gross_value',
                            'movies': 'movies_starred_in'}
MOVIE_JSON_TO_NODE_DICT = {'name': 'name',
                            'box_office': 'gross_value',
                            'year': 'year_released',
                            'actors': 'actors'}

app = Flask(__name__)  # The flask API object
app.config.from_object(__name__)  # Load the dicts above into the API environment


def filter_list(list_to_filter, attr, attr_value, list_type):
    """
    Utility function to filter a given list based on the whether it has the given
    values for the given attributes. Keeps the objects where all the objects have the
    given attr_vals for the corresponding attrs.
    :param list_to_filter: The list of objects to filter.
    :param attr: The attribute to filter on.
    :param attr_value: The value to filter for,
    :param list_type: "actor" or "movie"
    :return: Filtered list with only objects that have the given attribute value for the given attribute.
    """
    if list_type == "actor" and attr not in ACTOR_JSON_TO_NODE_DICT:
        return []
    elif list_type == "movie" and attr not in MOVIE_JSON_TO_NODE_DICT:
        return []
    dict_to_use = ACTOR_JSON_TO_NODE_DICT if list_type == "actor" else MOVIE_JSON_TO_NODE_DICT
    filtered_list = []
    for i, item in enumerate(list_to_filter):
        item = item.__dict__ if type(item) != dict else item
        if str(item[dict_to_use[attr]]) == str(attr_value):
            filtered_list.append(item)
    return filtered_list


def filter_list_or(list_to_filter, attrs, attr_vals, list_type):
    """
    Utility function to filter a list based on whether the object has any of the attribute values
    for the given attributes. Keeps the objects in which atleast one attr_vals matches the
    given ones for the given attrs.
    :param list_to_filter: The list of objects to filter
    :param attrs: The attributes to filter on
    :param attr_vals: The values to filter for
    :param list_type: "actor" or "movie"
    :return: A list of objects with at least one of the attributes matching the corresponding attribute values.
    """
    if list_type == "actor" and False in [(attr in ACTOR_JSON_TO_NODE_DICT) for attr in attrs]:
        return []
    if list_type == "movie" and False in [(attr in MOVIE_JSON_TO_NODE_DICT) for attr in attrs]:
        return []
    dict_to_use = ACTOR_JSON_TO_NODE_DICT if list_type == "actor" else MOVIE_JSON_TO_NODE_DICT
    filtered_list = []
    for i, item in enumerate(list_to_filter):
        item = item.__dict__ if type(item) != dict else item
        if True in [(str(item[dict_to_use[attr]]) == str(attr_val)) for attr, attr_val in zip(attrs, attr_vals)]:
            filtered_list.append(item)
    return filtered_list


def or_get_request_helper(attr1, attr_val1, attr2, attr_val2, orig_dict, list_type: str):
    """
    Helper function to handle an OR GET request on the API.
    Returns list of objects where atleast one of the attrs has the
    right attr_val.
    :param attr1: first attribute
    :param attr_val1: value for first attribute
    :param attr2: second attribute
    :param attr_val2: value for second attribute
    :param orig_dict: Dictionary (name --> GraphNode)
    :param list_type: "actor" or "movie"
    :return: list of objects that match the query
    """
    items_matching_request = orig_dict.values()
    attr_val1 = attr_val1.replace("_", " ")
    attr_val2 = attr_val2.replace("_", " ")
    items_matching_request = filter_list_or(items_matching_request, [attr1, attr2], [attr_val1, attr_val2], list_type)
    return items_matching_request


def and_get_request_helper(attr_dict, orig_dict, type: str):
    """
    Helper function to handle GET queries.
    Returns list of objects which satisfy all the given attribute requirements.
    :param attr_dict: Dictionary of attributes to attribute values
    :param orig_dict: The dictionary (name --> GraphNode) to search in
    :param type: "actor" or "movie"
    :return: list of objects satisfying all the attribute conditions
    """
    items_matching_request = orig_dict.values()
    for attr, attr_val in attr_dict.items():
        attr_val = attr_val.replace('_', " ")
        # print(attr, attr_val)
        items_matching_request = filter_list(items_matching_request, attr, attr_val, type)
    return items_matching_request


# OPTIONS Requests:


@app.route('/', methods=['OPTIONS'])
def handle_options_request():
    """
    Handler for OPTIONS request.
    :return: Response to the OPTIONS request
    """
    response_string = "Allow: GET, PUT, POST, DELETE, OPTIONS\nTwo sub-APIs: 'movies' and 'actors'"
    return make_response(jsonify(response_string), 200)


@app.route('/', methods=["GET"])
def index():
    """
    Main Page Message.
    :return: Response to an empty GET request on the home page.
    """
    return make_response(jsonify("Welcome to the Hollywood Database."), 200)


# GET Requests:

@app.route('/actors/<string:attr1>=<string:attr_val1>|<string:attr2>=<attr_val2>', methods=['GET'])
def handle_actor_or_get_request(attr1, attr_val1, attr2, attr_val2):
    """
    Handler for OR GET requests on the actors API
    :param attr1: first attribute to filter on
    :param attr_val1: value of first attribute to filter on
    :param attr2: second attribute to filter on
    :param attr_val2: value of second attribute to filter on
    :return: JSON representation of actor nodes satisfying the query if valid request.
    """
    actors_matching_query = or_get_request_helper(attr1, attr_val1, attr2, attr_val2, ACTORS, "actor")
    return make_response(jsonify(actors_matching_query),
                         200 if len(actors_matching_query) > 0 else 400)


@app.route('/movies/<string:attr1>=<string:attr_val1>|<string:attr2>=<attr_val2>', methods=['GET'])
def handle_movies_or_get_request(attr1, attr_val1, attr2, attr_val2):
    """
    Handler for OR GET requests on the movies API
    :param attr1: first attribute to filter on
    :param attr_val1: value of first attribute to filter on
    :param attr2: second attribute to filter on
    :param attr_val2: value of second attribute to filter on
    :return: JSON representation of movie nodes satisfying the query if valid request.
    """
    movies_matching_query = or_get_request_helper(attr1, attr_val1, attr2, attr_val2, MOVIES, "movie")
    return make_response(jsonify(movies_matching_query),
                         200 if len(movies_matching_query) > 0 else 400)


@app.route('/actors/<string:name>', methods=['GET'])
def handle_get_actor_request(name):
    """
    Handler for GET query on the actors API.
    :param name: Name of the actor to get information about
    :return: JSON representation of actor node if valid request.
    """
    name = name.replace("_", " ")
    # print(name)
    if name in ACTORS:
        return make_response(jsonify(ACTORS[name].__dict__), 200)
    return make_response(jsonify("Couldn't find the actor in our database."), 400)


@app.route('/movies/<string:name>', methods=['GET'])
def handle_get_movie_request(name):
    """
    Handler for GET query on the movies API.
    :param name: Name of the movie to get information about
    :return: JSON representation of movie node if valid request.
    """
    name = name.replace("_", " ")
    # print(name)
    if name in MOVIES:
        return make_response(jsonify(MOVIES[name].__dict__), 200)
    return make_response(jsonify("Couldn't find the movie in our database."), 400)


@app.route('/actors/', methods=['GET'])
def handle_actor_and_get_request():
    """
    Handler for GET requests on the actors API
    :return: JSON representation of actor nodes satisfying the query if valid request.
    """

    attr_dict = request.args.to_dict()
    # print(attr_dict)
    actors_matching_query = and_get_request_helper(attr_dict, ACTORS, "actor")
    return make_response(jsonify(actors_matching_query),
                         200 if len(actors_matching_query) > 0 else 400)


@app.route('/movies/', methods=['GET'])
def handle_movie_and_get_request():
    """
    Handler for GET requests on the movies API
    :return: JSON representation of movie nodes satisfying the query if valid request.
    """
    attr_dict = request.args.to_dict()
    # print(attr_dict)
    movies_matching_query = and_get_request_helper(attr_dict, MOVIES, "movie")
    return make_response(jsonify(movies_matching_query),
                         200 if len(movies_matching_query) > 0 else 400)


# PUT Requests:


def update_list(orig_dict, name, r_json, conversion_dict):
    """
    Helper function for PUT requests. Updates objects based on a dictionary with updated
    values for its variables.
    :param orig_dict: The dictionary to look the object in. (Name --> Node)
    :param name: Name of the object
    :param r_json: Updated values. Dict (Attribute --> Updated value for the attribute)
    :param conversion_dict: Dictionary to help translate between API attribute list
    and object variable names.
    :return: 201 response if update was successful, else 400 bad request.
    """
    if False in [(attr in conversion_dict) for attr in r_json]:
        return make_response(jsonify("Invalid Request"), 400)
    item_orig = orig_dict[name].__dict__
    for attr, attr_val in r_json.items():
        item_orig[conversion_dict[attr]] = attr_val
    orig_dict[name].update(item_orig)
    return make_response(jsonify("Updated Successfully"), 201)


@app.route('/actors/<string:name>', methods=["PUT"])
def handle_actor_put_request(name):
    """
    Handler for PUT requests on the Actors API.
    :param name: Name of the movie to update.
    :return: 200 status response if successful, else 400 bad request.
    """
    name = name.replace("_", " ")
    if (name not in ACTORS) or (not request.json):
        return make_response(jsonify("Bad Request"), 400)
    return update_list(ACTORS, name, request.json, ACTOR_JSON_TO_NODE_DICT)


@app.route('/movies/<string:name>', methods=['PUT'])
def handle_movie_put_request(name):
    """
    Handler for PUT requests on the Movies API.
    :param name: Name of the movie to update.
    :return: 200 status response if successful, else 400 bad request.
    """
    name = name.replace("_", " ")
    if (name not in MOVIES) or (not request.json):
        return make_response(jsonify("Bad Request"), 400)
    return update_list(MOVIES, name, request.json, MOVIE_JSON_TO_NODE_DICT)


# POST Requests:


def add_to_list(orig_dict, name, r_json, conversion_dict, class_type):
    """
    Utility function to add objects to the API database.
    :param orig_dict: Dictionary to add to.
    :param name: Name of the object.
    :param r_json: Dictionary with attributes and attribute values.
    :param conversion_dict: Dictionary to convert JSON attributes to class variable names
    :param class_type: The type of object to create.
    :return: 201 successful update response (if valid request), else 400 bad request.
    """
    if False in [(attr in conversion_dict) for attr in r_json]:
        return make_response(jsonify("Invalid Request"), 400)
    new_obj = class_type("", "", "")
    new_obj_dict = new_obj.__dict__
    for attr, attr_val in r_json.items():
        new_obj_dict[conversion_dict[attr]] = attr_val
    new_obj.update(new_obj_dict)
    orig_dict[name] = new_obj
    return make_response(jsonify("Added successfully."), 201)


@app.route('/actors/<string:name>', methods=['POST'])
def handle_actor_post_request(name):
    """
    Handler for POST requests on the Actors API.
    :param name: Name of the actor to add.
    :return: 201 successful update response (if valid request), else 400 bad request.
    """
    name = name.replace("_", " ")
    if not request.json:
        return make_response(jsonify("Bad Request"), 400)
    if name in ACTORS:
        return update_list(ACTORS, name, request.json, ACTOR_JSON_TO_NODE_DICT)
    else:
        return add_to_list(ACTORS, name, request.json, ACTOR_JSON_TO_NODE_DICT, Actor)


@app.route('/movies/<string:name>', methods=['POST'])
def handle_movie_post_request(name):
    """
    Handler for POST requests on the Movies API.
    :param name: Name of the movie to add.
    :return: 201 successful update response (if valid request), else 400 bad request.
    """
    name = name.replace("_", " ")
    if not request.json:
        return make_response(jsonify("Bad Request"), 400)
    if name in MOVIES:
        return update_list(MOVIES, name, request.json, MOVIE_JSON_TO_NODE_DICT)
    else:
        return add_to_list(MOVIES, name, request.json, MOVIE_JSON_TO_NODE_DICT, Movie)


# DELETE Requests:


@app.route('/actors/<string:name>', methods=['DELETE'])
def handle_actor_delete_request(name):
    """
    Handler for DELETE requests on the actors API.
    :param name: name of the actor to delete.
    :return: 201 if deleted successfully, or 400 if bad request.
    """
    name = name.replace("_", " ")
    if name in ACTORS:
        del ACTORS[name]
        return make_response(jsonify("Deleted Successfully"), 201)
    else:
        return make_response(jsonify("Actor not in database."), 400)


@app.route('/movies/<string:name>', methods=['DELETE'])
def handle_movie_delete_request(name):
    """
    Handler for DELETE requests on the movies API.
    :param name: name of the movie to delete.
    :return: 201 if deleted successfully, or 400 if bad request.
    """
    name = name.replace("_", " ")
    if name in MOVIES:
        del MOVIES[name]
        return make_response(jsonify("Deleted Successfully"), 201)
    else:
        return make_response(jsonify("Movie not in database."), 400)


def __main__():
    app.run(debug=True)


if __name__ == '__main__':
    __main__()


