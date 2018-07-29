from venv.Graph import make_graph
from venv.DataAnalysis import extract_from_json
import networkx as nx
import matplotlib.pyplot as plt
from venv.helper import get_node_attrs, create_graph, get_movies_of_actors

"""Reference: https://stackoverflow.com/questions/27030473/how-to-set-colors-for-nodes-in-networkx-python"""

NUM_MOVIES = 50
NUM_ACTORS = 50
FIG_SIZE = (50, 50)


def __main__():

    actors, movies = extract_from_json('data.json', NUM_MOVIES, NUM_ACTORS)  # Get the ACTORS and MOVIES dict
    actors, movies = make_graph(actors, movies)  # Draw the edges between these nodes
    # movies = get_movies_of_actors(actors)
    graph = nx.Graph()
    create_graph(graph, actors, movies)  # Add the nodes draw the edges between nodes in the networkx graph
    node_colors, node_sizes = get_node_attrs(graph)  # Get the node colors and sizes

    # Plot the graph
    plt.figure(figsize=FIG_SIZE)
    nx.draw_random(graph, node_color=node_colors, node_size=node_sizes, with_labels=True)
    plt.savefig('actor_movie_graph_random.png')

    plt.figure(figsize=FIG_SIZE)
    nx.draw(graph, node_color=node_colors, node_size=node_sizes, with_labels=True)
    plt.savefig('actor_movie_graph.png')


if __name__ == '__main__':
    __main__()
