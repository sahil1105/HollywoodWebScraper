from venv.Graph import Actor, Movie


def get_node_attrs(graph) -> (list, list):
    """
    Utility function to get the colors and sizes to draw the graph with.
    Actor nodes are drawn blue and Movie nodes are drawn green. Node size depends
    on the length of these nodes' string representation.
    :param graph: The graph
    :return: list of node colors and node sizes, respectively
    """
    node_colors = []
    node_sizes = []
    for node in graph:
        if isinstance(node, Actor):
            node_colors.append('blue')
        else:
            node_colors.append('green')
        node_sizes.append(400*len(node.__str__()))
    # edge_widths = [u.edge_weights[u.edges.index(v)]/10**6 for u, v in G.edges()]
    return node_colors, node_sizes


def create_graph(graph, actors, movies):
    """
    Utility function to create the graph from the given ACTORS and MOVIES dictionary.
    Adds nodes and edges to the given graph.
    :param graph: The graph to add nodes and edges to.
    :param actors: Dictionary (Name --> Node)
    :param movies: Dictionary (Name --> Node)
    :return: None, the passed in graph object is modified
    """
    graph.add_nodes_from([node for _, node in actors.items()])
    graph.add_nodes_from([node for _, node in movies.items()])

    for actor_node in actors.values():
        graph.add_weighted_edges_from([(actor_node, movie_node, 1)
                                       for movie_node, edge_weight in zip(actor_node.edges, actor_node.edge_weights)
                                       if movie_node in movies.values()])

    for movie_node in movies.values():
        graph.add_weighted_edges_from([(movie_node, actor_node, 1)
                                       for actor_node, edge_weight in zip(movie_node.edges, movie_node.edge_weights)
                                       if ((not graph.has_edge(actor_node, movie_node))
                                       and (actor_node in actors.values()))])


def get_movies_of_actors(actors):
    """
    Utility helper which gets all the movies that the actors in the 'actors'
    dict share within each other.
    :param actors: Dict (Actor Name --> Actor Node)
    :return: Dict (Movie Name --> Movie Node)
    """
    movies_of_actors = set([])
    for actor_name, actor_node in actors.items():
        actor_movies = actor_node.edges  # Get the movies of this actor
        for movie_node in actor_movies:
            # If this movies has at least 2 actors in the current actor set, then add it
            if len(set(movie_node.edges).intersection(actors.values())) > 1:
                movies_of_actors.add(movie_node)
    movies_of_actors = {movie_node.name: movie_node for movie_node in movies_of_actors}  # Convert to a dict
    return movies_of_actors
