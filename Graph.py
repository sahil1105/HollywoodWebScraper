
class GraphNode:
    """
    Generic Parent Class whose instances will serve as the nodes in the final graph.
    Contains of a list of edges, their corresponding weights and functions to add,
    remove these attributes.
    @author sahil1105
    """

    def __init__(self):
        """
        Constructor for a GraphNode instance. Initializes a list of edges,
        i.e. a list of references to other GraphNode instances that it is connected to.
        Stores the corresponding weights for each weight in a separate list with the
        same indexing.
        """
        self.edges = []
        self.edge_weights = []

    def get_edges(self):
        """
        Getter for the edges of the GraphNode i.e. a list of references to other
        GraphNode objects that it is connected to.
        :return: list of edges
        """
        return self.edges

    def get_edge_weight(self, graph_node):
        """
        Get the edge weight of the edge between this GraphNode and given GraphNode, if there is one.
        :param graph_node: The GraphNode on the other side of the edge
        :return: weight of the edge between the nodes if there is one, else -1
        """
        if graph_node in self.edges:
            return self.edge_weights[self.edges.index(graph_node)]
        return -1

    def add_edge(self, graph_node, edge_weight):
        """
        Add an edge between this GraphNode and the given GraphNode if there already isn't one.
        If there is already one, the edge weight is updated if it is different.
        :param graph_node: GraphNode to add an edge with.
        :param edge_weight: Weight of the to be edge between the two nodes.
        :return: self
        """
        if graph_node not in self.edges:
            self.edges.append(graph_node)
            self.edge_weights.append(edge_weight)
        if self.edge_weights[self.edges.index(graph_node)] != edge_weight:
            self.edge_weights[self.edges.index(graph_node)] = edge_weight

    def remove_edge(self, graph_node):
        """
        Removes an edge between this node and the given node if there is one
        :param graph_node: The GraphNode to remove an edge with
        :return: self
        """
        if graph_node in self.edges:
            idx = self.edges.index(graph_node)
            self.edges.pop(idx)
            self.edge_weights.pop(idx)

    def __str__(self):
        """
        Overriding the string representation to aid debugging
        :return: String representation of a GraphNode.
        """
        return "EDGES: {}, EDGE_WEIGHTS: {}".format(self.edges, self.edge_weights)

    def update(self, new_data):
        print(new_data)
        for key, value in new_data.items():
            setattr(self, key, value)


class Movie(GraphNode):
    """
    Child class of the GraphNode class which is meant to hold details about a Movie.
    Holds information such as its name, the year of its release, its gross value
    (box office collection) and ACTORS that starred in it.
    @author sahil1105
    """
    def __init__(self, name: str, year_released: int, gross_value: float):
        """
        Constructor for a Movie Node.
        :param name: name of the movie
        :param year_released: year it was released in
        :param gross_value: the gross value of the movie
        """
        GraphNode.__init__(self)
        self.name = name
        self.actors = []
        self.year_released = year_released
        self.gross_value = gross_value

    def add_actor(self, actor):
        """
        Add an actor to the list of ACTORS that starred in the movie, if he/she isn't already there.
        :param actor: The actor to add
        :return: self
        """
        if actor not in self.actors:
            self.actors.append(actor)

    def remove_actor(self, actor):
        """
        Remove an actor from the list of starring ACTORS, if he/she is there to begin with.
        :param actor: The actor to remove.
        :return: self
        """
        if actor in self.actors:
            self.actors.remove(actor)

    def __eq__(self, other):
        """
        Overriding the equivalency check function (==, is, etc.) to compare two Movie Nodes.
        :param other: The Movie node to compare this Movie Node to
        :return: True if the two MOVIES are the same, False otherwise.
        """
        if self.name == other.name and self.year_released == other.year_released:
            return True
        return False

    def __ne__(self, other):
        """
        Overriding the not equal function. Essentially is !__eq__(self, other).
        :param other: The Movie node to compare this Movie node to.
        :return: True if the Movie nodes are not the same, False otherwise.
        """
        return not __eq(self, other)

    def __str__(self):
        """
        Overriding string representation of the Movie Node.
        :return: String representation of the Movie Node.
        """
        return "{}\n{}\n${}".format(self.name, self.year_released, self.gross_value)

    def __hash__(self):
        """
        Implementing hash functionality so these nodes can be used with graph libraries
        :return: hash value of the class instance
        """
        return hash(self.name)


class Actor(GraphNode):
    """
    Child class of a GraphNode to store the details of a Actor like his/her name, age and MOVIES
    he/she has starred in.
    @author sahil1105
    """
    def __init__(self, name: str, age: int, gross_value=None):
        """
        Constructor for the Actor Node class.
        :param name: Name of the actor.
        :param age: Age of the actor.
        """
        GraphNode.__init__(self)
        self.name = name
        self.movies_starred_in = []
        self.age = age
        self.gross_value = gross_value

    def add_movie(self, movie: str):
        """
        Add a movie to the actor's portfolio if it isn't already there.
        :param movie: The name of the movie to add
        :return: self
        """
        if movie not in self.movies_starred_in:
            self.movies_starred_in.append(movie)

    def remove_movie(self, movie: str):
        """
        Remove a movie from the actor's portfolio.
        :param movie: Name of the movie to remove
        :return: self
        """
        if movie in self.movies_starred_in:
            self.movies_starred_in.remove(movie)

    def get_grossing_value(self):
        """
        Find how much the actor grossed from all his MOVIES. Done by summing up the weights of
        all its edges. Hence should only be called after the Graph has been formed.
        :return: Grossing Value of the actor.
        """
        if self.gross_value is None:
            self.gross_value = sum(self.edge_weights)
        return self.gross_value

    def __eq__(self, other):
        """
        Overriding equivalency comparison between this Actor and another.
        :param other: The Actor node to compare with.
        :return: True if the Actors are the same, else False.
        """
        if self.name == other.name and self.age == other.age:
            return True
        return False

    def __ne__(self, other):
        """
        Overriding not equal comparison. Essentially the negation of the __eq__ function.
        :param other: The Actor node to compare with.
        :return: True if Actors are not the same, False otherwise.
        """
        return not __eq__(self, other)

    def __str__(self):
        """
        Overriding the string representation of the Actor class.
        :return: String representation of the Actor Node.
        """
        return "{}\n{}y/o".format(self.name, self.age)

    def __hash__(self):
        """
        Implementing hash functionality so these nodes can be used with graph libraries
        :return: hash value of the class instance
        """
        return hash(self.name)


def json_default(o):
    """
    Defining the default behavior of conversion of a class to a JSON-able object.
    Essentially makes a dictionary out of the class and returns it. Returns a list of
    all its elements in case of a set.
    :param o: The object to convert to JSON.
    :return: JSON-able version of the class.
    """
    if isinstance(o, set):
        return list(o)
    return o.__dict__


def calc_edge_weights(movie_node, actor_node=None):
    """
    Calculate the edge weights to assign to a Movie node's edges based on its gross value.
    :param movie_node: The Movie Node
    :return: List of weights to apply to its edges.
    """
    num_edges = len(movie_node.edges)
    gross_value = movie_node.gross_value
    edge_weights = [gross_value/(i+1) for i in range(num_edges)]  # Makes sure that ACTORS higher have higher weights
    return edge_weights


def make_graph(actors, movies, edge_weight_func=calc_edge_weights):
    """
    Construct a graph out of the given ACTORS and MOVIES.
    :param actors: A dictionary (name of actor --> Actor Node for the actor)
    :param movies: A dictionary (name of the movie --> Movie Node for the movie)
    :return: Modified dictionaries ACTORS and MOVIES where there are edges between the ACTORS
    and MOVIES wherever possible along with appropriate weights.
    """
    # Draw edges from ACTORS to MOVIES (and the other way round) if one of its MOVIES has a node.
    make_edges_from_actors_to_movies(actors, movies)

    # Draw edges from MOVIES to ACTORS (and the other way around) if one its ACTORS has a node.
    make_edges_from_movies_to_actors(actors, movies)

    # Assign appropriate weights to the edges.
    assign_weights_to_edges(movies, edge_weight_func)

    return actors, movies


def assign_weights_to_edges(movies, edge_weight_func=calc_edge_weights):
    """
    Utility function to assign weights to all the edges between the Movie Nodes
    and the Actor Nodes they are connected to.
    :param movies: Dictionary (name of the movie --> Movie Node for the movie)
    :return: Nothing.
    """
    for _, movie_node in movies.items():
        edge_weights = edge_weight_func(movie_node)
        for i, actor_node in enumerate(movie_node.edges):
            movie_node.edge_weights[i] = edge_weights[i]
            actor_node.add_edge(movie_node, edge_weights[i])


def make_edges_from_movies_to_actors(actors, movies):
    """
    Utility function to draw edges between MOVIES and ACTORS that have starred in them,
    if one doesn't already exist.
    :param actors: Dictionary (name of actor --> Actor node)
    :param movies: Dictionary (name of the movie --> Movie Node for the movie)
    :return: Nothing.
    """
    for movie_name, movie_node in movies.items():
        for actor_name in movie_node.actors:
            if actor_name in actors:
                # Add the edge in the Movie Node
                movie_node.add_edge(actors[actor_name], movie_node.gross_value)
                # If this movie isn't already in actor's portfolio, then add it
                if movie_name not in actors[actor_name].movies_starred_in:
                    actors[actor_name].add_movie(movie_name)
                # Add the edge in the Actor Node as well
                actors[actor_name].add_edge(movie_node, movie_node.gross_value)


def make_edges_from_actors_to_movies(actors, movies):
    """
    Utility function to draw edges between ACTORS and the MOVIES they have starred in,
    if one doesn't already exist.
    :param actors: Dictionary (name of actor --> Actor node)
    :param movies: Dictionary (name of the movie --> Movie Node for the movie)
    :return: Nothing.
    """
    for actor_name, actor_node in actors.items():
        for movie_name in actor_node.movies_starred_in:
            if movie_name in movies:
                # Add the edge in the Actor node
                actor_node.add_edge(movies[movie_name], movies[movie_name].gross_value)
                # If actor doesn't exist in Movie's cast list, then add it
                if actor_name not in movies[movie_name].actors:
                    movies[movie_name].add_actor(actor_name)
                # Add the edge in the Movie Node as well
                movies[movie_name].add_edge(actor_node, movies[movie_name].gross_value)


# QUERIES


def get_movie_gross_value(movies, movie_name):
    """
    Query helper to find the gross value of a movie, if the movie exists in the Graph.
    :param movies: Dictionary (name of the movie --> Movie Node for the movie)
    :param movie_name: Name of the movie to get gross value of.
    :return: Gross value of the movie, if a node for it exists, else -1
    """
    if movie_name in movies:
        return movies[movie_name].gross_value
    return -1


def get_movies_starred_in(actors, actor_name):
    """
    Query helper to get the MOVIES an actor has starred in.
    :param actors: Dictionary (name of actor --> Actor node)
    :param actor_name: Name of the actor to get the MOVIES for.
    :return: List of MOVIES an actor has starred in, if there exists a node for him/her
    in the graph, else an empty list is returned.
    """
    if actor_name in actors:
        return actors[actor_name].movies_starred_in
    return []


def get_starred_actors(movies, movie_name):
    """
    Query helper to get the ACTORS that have starred in a movie.
    :param movies: Dictionary (name of the movie --> Movie Node for the movie)
    :param movie_name: Name of the movie to get the ACTORS for.
    :return: List of ACTORS that have starred in the movie if there exists a node for it,
    else an empty list.
    """
    if movie_name in movies:
        return movies[movie_name].actors
    return []


def n_highest_grossing_actors(actors, n):
    """
    Query helper to get the the n highest grossing ACTORS
    :param actors: Dictionary (name of actor --> Actor node)
    :param n: Number of highest grossing ACTORS to find
    :return: List of n highest grossing ACTORS, sorted highest to lowest. If n > length of ACTORS,
    all the ACTORS are returned ordered highest to lowest in terms of grossing value.
    """
    actors_sorted_by_gross_value = sorted(actors, key=lambda x:actors[x].get_grossing_value(), reverse=True)
    return actors_sorted_by_gross_value[:min(n, len(actors_sorted_by_gross_value))]


def n_oldest_actors(actors, n):
    """
    Query helper to get the n oldest ACTORS out of the given graph.
    :param actors: Dictionary (name of actor --> Actor node)
    :param n: The number of oldest ACTORS to find.
    :return: List of n oldest ACTORS, ordered oldest to youngest. If n > length
    of ACTORS dictionary, then all the ACTORS are returned, ordered oldest to
    youngest.
    """
    actors_sorted_by_age = sorted(actors, key=lambda x: actors[x].age, reverse=True)
    return actors_sorted_by_age[:min(n, len(actors_sorted_by_age))]


def get_movies_in_a_year(movies, year):
    """
    Query helper to get all the MOVIES that released that year.
    :param movies: Dictionary (name of the movie --> Movie Node for the movie)
    :param year: The year to look for MOVIES in.
    :return: List of MOVIES that released in the given year.
    """
    movies_in_year = [movie_name for movie_name, movie_node in movies.items() if movie_node.year_released == year]
    return movies_in_year


def get_actors_in_a_year(movies, year):
    """
    Query helper to find the ACTORS that starred in some movie released in the given year.
    :param movies: Dictionary (name of the movie --> Movie Node for the movie)
    :param year: Year to look for MOVIES in.
    :return: List of ACTORS that starred in some movie released in the given year.
    """
    movies_in_year = get_movies_in_a_year(movies, year)  # Get all the movie released that year
    actors_in_year = set([])
    for movie in movies_in_year:
        actors_in_year = actors_in_year.union(set(movies[movie].actors))  # Get all the ACTORS in those MOVIES
    actors_in_year = list(actors_in_year)  # Convert the set into a list
    return actors_in_year