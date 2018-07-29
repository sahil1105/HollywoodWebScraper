from venv.Graph import Actor, Movie, make_graph
import json
import matplotlib.pyplot as plt
import sys
from venv.helper import create_graph, get_node_attrs, get_movies_of_actors
import networkx as nx


def get_actor_node_from_json_object(json_object):
    """
    Utility function to extract information from a json object and return the underlying actor's
    information in the form of an Actor GraphNode.
    :param json_object: json_object containing actor's information, must have the fields:
    'name', 'age', 'total_gross', 'MOVIES'.
    :return: An Actor GraphNode encapsulating the information extracted from the json object.
    """
    new_actor = Actor(json_object['name'], json_object['age'], json_object['total_gross'])
    new_actor.movies_starred_in = json_object['movies']
    return new_actor


def get_movie_node_from_json_object(json_object):
    """
    Utility function to extract information from a json object and return the underlying movie's
    information in the form of an Movie GraphNode.
    :param json_object: json_object containing movie's information, must have the fields:
    'name', 'year', 'box_office', 'ACTORS'.
    :return: An Movie GraphNode encapsulating the information extracted from the json object.
    """
    new_movie = Movie(json_object['name'], json_object['year'], json_object['box_office'])
    new_movie.actors = json_object['actors']
    return new_movie


def extract_from_json(filename: str = 'data.json',
                      max_num_actors: int = sys.maxsize, max_num_movies: int = sys.maxsize) -> (dict, dict):
    """
    Utility function to extract the Movies and Actors from the given JSON file.
    Converts them into two dictionaries, one of actors and another of movies.
    :param filename: name of the json file
    :param max_num_actors: max number of ACTORS to return, default: no limit
    :param max_num_movies: max number of MOVIES to return, default: no limit
    :return: Dict (Actor Name --> Actor Node), Dict (Movie Name --> Movie Node)
    """
    actors = []
    movies = []
    num_actors_added = 0
    num_movies_added = 0

    with open(filename, 'r') as file:
        json_data = json.load(file)
        for json_dict in json_data:
            for name, json_object in json_dict.items():
                if json_object['json_class'] == "Actor" and num_actors_added < max_num_actors:
                    actors.append(get_actor_node_from_json_object(json_object))
                    num_actors_added += 1
                elif json_object['json_class'] == "Movie" and num_movies_added < max_num_movies:
                    movies.append(get_movie_node_from_json_object(json_object))
                    num_movies_added += 1

    actors = {node.name: node for node in actors}
    movies = {node.name: node for node in movies}
    return actors, movies


def get_hub_actors(actors: dict, n: int = 10) -> list:
    """
    Utility function to get the 'n' ACTORS with most connection to other ACTORS.
    Requires that graph between the MOVIES and ACTORS has been made.
    Does a basic level-2 search of the graph from each actor node.
    :param actors: Dictionary (Actor name --> Actor Node)
    :param n: Number of top hub ACTORS to find
    :return: Top n hub actors
    """
    actor_connections_dict = {}
    for actor_node in actors.values():
        connections = set([])
        for movie_node in actor_node.edges:
            connections = connections.union(set(movie_node.actors))
        actor_connections_dict[actor_node.name] = len(connections)
    return sorted(actor_connections_dict, key=actor_connections_dict.get, reverse=True)[:min(len(actors.keys()), n)]


def plot_hub_actors(hub_actors, plot=True):
    """
    Utility function to plot the given hub actors and the movies they share.
    :param hub_actors: Dict (Actor Name --> Actor Node)
    :param plot: True if you want to plot it
    :return: None
    """
    movies_of_hub_actors = get_movies_of_actors(hub_actors)  # Get the movies shared between these actors
    graph = nx.Graph()
    create_graph(graph, hub_actors, movies_of_hub_actors)  # Add nodes and edges to the graph
    node_colors, node_sizes = get_node_attrs(graph)  # Get the attributes to for plotting
    if plot:
        plt.figure(figsize=(25, 25))
        nx.draw(graph, node_color=node_colors, node_size=node_sizes, with_labels=True)
        plt.show()


def plot_age_grossing_scatter(actors, plot=True):
    """
    Utility function to plot a scatter plot of ACTORS' ages vs their total gross value.
    :param actors: Dictionary (Actor name --> Actor Node)
    :param plot: True if you want to plot it
    :return: None
    """
    # fig, ax = plt.subplots()
    ages = []
    grossing = []
    for actor_node in actors.values():
        ages.append(actor_node.age)
        grossing.append(actor_node.gross_value)
    # ax.scatter(ages, grossing)
    plt.scatter(ages, grossing)
    plt.xlabel("Age")
    plt.ylabel("Gross Value")
    if plot: plt.show()


def plot_age_num_movies_scatter(actors, plot=True):
    """
    Utility function to plot a scatter plot of ACTORS' ages vs the number of MOVIES they've acted in.
    :param actors: Dictionary (Actor name --> Actor Node)
    :param plot: True if you want to plot it
    :return: None
    """
    ages = []
    num_movies = []
    for actor_node in actors.values():
        ages.append(actor_node.age)
        num_movies.append(len(actor_node.movies_starred_in))
    plt.scatter(ages, num_movies)
    plt.xlabel("Age")
    plt.ylabel("Number of Movies Starred In")
    if plot: plt.show()


def plot_year_num_movies(movies, plot=True):
    """
    Utility function to plot a line graph of the year vs the number of MOVIES released that year.
    :param movies: Dictionary (Movie Name --> Movie Node)
    :param plot: True if you want to plot it
    :return: None
    """
    year_num_movies = {}
    for movie_node in movies.values():
        if movie_node.year_released in year_num_movies:
            year_num_movies[movie_node.year_released] += 1
        else:
            year_num_movies[movie_node.year_released] = 1
    years = []
    num_movies = []
    for year, num_movie in sorted(year_num_movies.items(), key=lambda x: x[0]):
        if year > 1500:
            years.append(year)
            num_movies.append(num_movie)
    plt.plot(years, num_movies)
    plt.xlabel("Year")
    plt.ylabel("Number of Movies Released")
    if plot: plt.show()


def get_average_gross_value_per_movie(actors: dict) -> float:
    """
    Utility function to calculate the average gross value of actors in a given dictionary, per movie
    :param actors: Dictionary (Actor Name --> Actor Node)
    :return: Average Gross Value of the actors
    """
    total_gross_value = sum([actor_node.gross_value/(len(actor_node.movies_starred_in)+1)
                             for actor_node in actors.values()])
    return total_gross_value/len(actors)


def __main__():

    actors, movies = extract_from_json('data.json')  # Get the data
    actors, movies = make_graph(actors, movies)  # Form the edges between the actors and movies
    hub_actors = get_hub_actors(actors, 10)  # Get the top 10 hub actors
    hub_actors = {actor_name: actors[actor_name] for actor_name in hub_actors}  # Convert to a dict
    plot_hub_actors(hub_actors)  # Plot the hub actors
    print("The hub actors are:", hub_actors.keys())
    print("Average Gross Income of Hub Actors:", get_average_gross_value_per_movie(hub_actors))
    print("Average Gross Income of All Actors:", get_average_gross_value_per_movie(actors))
    # Other analysis
    plot_age_grossing_scatter(actors)
    plot_age_num_movies_scatter(actors)
    plot_year_num_movies(movies)


if __name__ == '__main__':
    __main__()
