""""
References:
1. https://adesquared.wordpress.com/2013/06/16/using-python-beautifulsoup-to-scrape-a-wikipedia-table/
2. https://pythontips.com/2013/08/08/storing-and-loading-data-with-json/
3. https://stackoverflow.com/questions/8421922/how-do-i-convert-a-currency-string-to-a-floating-point-number-in-python
"""

# Import statements
from Graph import GraphNode, Actor, Movie, json_default, make_graph
from bs4 import BeautifulSoup as bs
import logging
from time import sleep, time
import requests as rq
import json
from re import sub
from decimal import Decimal
import jsonpickle


# Constants
WIKIPEDIA_URL = "https://en.wikipedia.org"
START = "/wiki/Morgan_Freeman"
CURRENT_YEAR = 2018
SLEEP_TIME = 0.10
LOG_FILE = "scraper_log.txt"
MOVIE_QUEUE = []
ACTOR_QUEUE = []
ACTORS = {}
MOVIES = {}
ACTORS_LIMIT = 300
MOVIES_LIMIT = 150


def scrape_movie_page(name: str, link: str):
    """
    Utility function to scrape a movie page.
    :param name: Name of the movie.
    :param link: Link to scrape.
    :return: A Movie Node containing the details of the movie and
    a dictionary (Name of actors who starred in the movie --> Link to actor's wiki page)
    """
    logging.info("scrape_movie_page called with name: {} and link: {}".format(name, link))

    actor_links = {}
    movie_details = None

    page = rq.get(link)  # Try to get the web page
    # If unsuccessful, log a warning and return None and empty dict
    if page is None or page.status_code != 200:
        logging.warning("Unable to scrape the link {} for the movie {}. "
                        "Received a non-200 status code".format(link, name))
        logging.info("Returning None and an empty dictionary")
        return movie_details, actor_links

    # If successful, use bs4 to parse the html page
    soup = bs(page.content, 'html.parser')

    release_date = get_release_date(soup)
    logging.debug("Release Date found to be: {}".format(release_date))
    gross_value = get_gross_value(soup)
    logging.debug("Gross Value found to be: {}".format(gross_value))
    actors, actor_links = get_starring_actors(soup)
    logging.debug("Found {} actors and found links for {} of them".format(len(actors), len(actor_links)))

    # If enough information was scraped from the page, then make a Movie Node
    if release_date is not None and gross_value is not None:
        year_released = int(release_date[:4])
        movie_details = Movie(name, year_released, gross_value)
        movie_details.actors = actors

    return movie_details, actor_links


def get_gross_value(soup):
    """
    Utility function to extract the Gross Value/ Box Office collection
    of a movie, from its html page.
    :param soup: BeautifulSoup Object
    :return: Gross Value of a movie, if it was extracted successfully, else None
    """
    logging.info("getGrossValue called.")

    # Isolate the info box object on the page
    info_table = soup.find('table', class_="infobox")

    # Find the row with the gross value information and extract from it
    try:
        rows = info_table.find_all('tr')
        for row in rows:
            if row.find('th') is not None and row.find('th').getText().strip() == 'Box office':
                box_office_details = row.find('td')
                gross_value = box_office_details.getText()
                gross_value = convert_currency_string_to_float(gross_value)  # Convert to a float value
                return gross_value
    except (Exception):
        logging.warning("Couldn't get gross value. Exception occurred during search. Returning None.")
        return None

    logging.info("Couldn't find the Box office details. Returning None.")
    return None


def convert_currency_string_to_float(money: str):
    """
    Utility function which gives a numerical representation of the given string
    containing a money value. Handles conversion from 'million'.
    :param money: String containing the money value
    :return: Float representing the money mentioned in the string.
    """
    logging.debug("convertCurrencyStringToFloat called with {}".format(money))
    in_million = False
    if "million" in money:  # Check if value is in millions
        in_million = True
        money = money[:money.index('million')]  # If it is, then remove everything including it and after

    # Convert to a float value, multiplying by 10**6 if it is in millions
    return float(Decimal(sub(r'[^\d.]', '', money)) * (10 ** 6 if in_million else 1))


def get_release_date(soup):
    """
    Utility function to extract the release date of a movie from its Wikipedia page.
    :param soup: BeautifulSoup object
    :return: String containing the release date of the movie in the yyyy-mm-dd format
    """
    logging.info("getReleaseDate called.")

    # Isolate the info box table on the html page
    info_table = soup.find('table', class_="infobox")

    # Find the row containing the release date and extract it if found
    try:
        rows = info_table.find_all('tr')
        for row in rows:
            if row.find('th') is not None and row.find('th').getText().strip() == "Release date":
                date_list = row.find('td')
                rl_date = date_list.find_all('li')[0]
                rl_date = rl_date.find('span', class_="bday")
                rl_date = rl_date.getText()
                return rl_date
    except(Exception):
        logging.warning("Couldn't find Release Date due to an exception. Returning None.")
        return None

    logging.info("Couldn't find Release Date details on the page. Returning None.")
    return None


def get_starring_actors(soup):
    """
    Utility function to extract the list of actors and links to their wikipedia pages,
    that starred in a movie from its wikipedia page.
    :param soup: BeautifulSoup object
    :return: List of Actors and Dictionary (Actor name --> Link to Wikipedia page)
    """
    logging.info("getStarringActors called.")
    actors = []
    actor_links = {}

    # Isolate the info box on the page
    info_table = soup.find('table', class_="infobox")

    # Find the row containing the movie's cast and parse these names and links to their wikipedia pages
    try:
        rows = info_table.find_all('tr')
        for row in rows:
            if row.find('th') is not None and row.find('th').getText().strip() == "Starring":
                actor_list = row.find('td')
                actor_list = row.find('div', class_="plainlist")
                actor_list = actor_list.find_all('li')
                for actor in actor_list:
                    try:
                        if actor.find('a') is not None:
                            actor_link = actor.find('a').get_attribute_list('href')[0]
                            actor_name = actor.find('a').getText()
                            actor_links[actor_name] = actor_link
                            actors.append(actor_name)
                    except (Exception):
                        logging.warning("Couldn't find a link for an actor due to an exception. "
                                        "Continuing on anyway.")
                        continue
                break
    except(Exception):
        logging.warning("An exception occurred while getting all actors and their links. "
                        "Returning actors that have been found so far.")
        return actors, actor_links

    return actors, actor_links


def scrape_actor_page(name: str, link: str):
    """
    Utility function to scrape an actor's wikipedia page and extract the required information.
    :param name: Name of the actor
    :param link: Link to the actor's wikipedia page
    :return: Actor Node with the parsed information and Dictionary (Names of movies they have starred in -->
    Links to these movies' wikipedia pages).
    """
    logging.info("scrape_actor_page called with name: {} and link: {}".format(name, link))

    movies = []
    movies_links = {}
    actor_details = None

    # Get the page
    page = rq.get(link)
    if page is None or page.status_code != 200:
        # If unable to get the page, then log an error and return None and an empty dict
        logging.error("Unable to scrape page for actor: {} from link: {} due to non-200 status code".format(name, link))
        return actor_details, movies_links

    # If successful, then scrape using the Beautiful Soup library
    soup = bs(page.content, 'html.parser')

    bday = get_birthday(soup)
    logging.info("Birthday found to be: {}".format(bday))
    if bday is not None:
        birth_year = int(bday[:4])
        actor_details = Actor(name, CURRENT_YEAR - birth_year)  # Get age by subtracting from current year

    # Get the filmography details of the actor
    try:
        filmography = soup.find(id="Filmography")

        # If details are in a list
        if filmography.find_next('div', class_="div-col columns column-width") is not None:
            logging.info("Filmography details are in a list.")
            movies, movies_links = get_films_list(filmography.find_next('div', class_="div-col columns column-width"))
        elif filmography.find_next('table', class_='wikitable') is not None:  # If details are in a table
            logging.info("Filmography details are in a table.")
            movies, movies_links = get_films_table(filmography.find_next('table', class_='wikitable'))
    except(Exception):
        logging.warning("Exception occured while getting filmography details.")
        return actor_details, movies_links

    if actor_details is not None:
        actor_details.movies_starred_in = movies

    logging.info("Found {} movies".format(len(movies)))

    return actor_details, movies_links


def get_birthday(soup):
    """
    Utility function to get the Birthday of an actor from his wikipedia page.
    :param soup: Beautiful Soup object
    :return: String containing the actor's birth date in yyyy-mm-dd format.
    """
    logging.info("getBirthday called.")

    # Isolate the info box table
    info_table = soup.find('table', class_="infobox")

    # Find the row containing the birth date and extract it
    try:
        rows = info_table.find_all('tr')
        for row in rows:
            if row.find('th') is not None and row.find('th').getText() == 'Born':
                bday_details = row.find('td')
                bday = bday_details.find('span', class_="bday")
                bday = bday.getText()
                #print(bday)
                return bday
    except(Exception):
        logging.warning("Exception occured while looking for BirthDate. Returning None.")
        return None

    return None


def get_title_index(header):
    """
    Utility function to get the index of the column that contains the titles of the movies
    the actor has starred in.
    :param header: The Beautiful Soup object containing the header row of the table (html).
    :return: The index of the column with heading 'Title', if found, else -1
    """
    logging.info("get_title_index called.")
    try:
        for i, col_heading in enumerate(header.find_all('th')):
            if col_heading.get_text() == 'Title':
                return i, len(header.find_all('th'))
    except(Exception):
        logging.warning("Couldn't find column for Title. Returning -1")
        return -1

    return -1


def get_films_list(filmography):
    """
    Utility function to extract names of movies and links to their wikipedia pages
    that an actor has starred in from a list on their wikipedia page.
    :param filmography: Beautiful Soup object containing the list.
    :return: A list of the name of the movies found and a Dictionary
    (Movie Name --> Link to movie's wikipedia page).
    """
    logging.info("getFilmsList called.")
    movie_links = {}
    movie_names = []

    filmography = filmography.find_all('li')
    for film in filmography:
        try:
            movie_name = film.find('a').get_attribute_list('title')[0]
            movie_link = film.find('a').get_attribute_list('href')[0]
            movie_names.append(movie_name)
            movie_links[movie_name] = movie_link
        except(Exception):
            logging.warning("Exception occurred while looking for a movie name or link. Continuing on.")
            continue

    return movie_names, movie_links


def get_films_table(filmography):
    """
    Utility function to extract names of movies and links to their wikipedia pages
    that an actor has starred in from a table on their wikipedia page.
    :param filmography: Beautiful Soup object containing the table.
    :return: A list of the name of the movies found and a Dictionary
    (Movie Name --> Link to movie's wikipedia page).
    """
    logging.info("getFilmsTable called.")
    movie_links = {}
    movie_names = []
    try:
        header = filmography.find_all('tr')[0]
        title_col_index, expected_n_cols = get_title_index(header)  # Get the column index with Movie Titles
        if title_col_index == -1:  # If not found, then return
            return movie_names, movie_links

        for row in filmography.find_all('tr')[1:]:
            cell = row.find_all('td')
            # To handle cases of rows across multiple vertical spaces
            if len(cell) == expected_n_cols:
                cell = cell[title_col_index]
            else:
                cell = cell[title_col_index-1]
            movie_name = cell.getText()
            try:
                movie_link = cell.find('a').get_attribute_list('href')[0]
                movie_name = cell.find('a').getText()
                movie_links[movie_name] = movie_link
                movie_names.append(movie_name)
            except (Exception):
                logging.warning("Exception occurred. Continuing on with the next movie.")
                continue
    except(Exception):
        logging.warning("Exception occurred while extracting names and links from the filmography table. Returning.")
        return movie_names, movie_links

    return movie_names, movie_links


def dump_graph_as_json(graph, fname = 'graph.json'):
    """
    Utility function to store the formed graph as a JSON string to a file.
    This method can handle circular references since it uses jsonpickle.
    :param graph: List of Movie and Actor Nodes.
    :param fname: File to store it to.
    :return: Name of file and a json encoding of the data that was stored in the file.
    """
    logging.info("dump_as_json called with filename: {}".format(fname))
    graph_json = jsonpickle.encode(graph)
    encoding_file = open(fname, 'w')
    encoding_file.writelines(graph_json)
    encoding_file.close()

    return fname, graph_json


def retrieve_graph_from_json(fname='graph.json'):
    """
    Utility function to retrieve data stored in a json file.
    This method can handle circular references since it uses jsonpickle.
    :param fname: Name of file to retrieve from.
    :return: Decoded list of Movie and Actor Nodes.
    """
    logging.info("retrieve_from_json called with filename: {}".format(fname))
    decoding_file = open(fname, 'r')
    decoded_graph = jsonpickle.decode(decoding_file.read())
    decoding_file.close()

    return decoded_graph


def dump_into_json(object, filename):
    """
    Utility function to dump the given object into json file of the given name
    :param object: The object to dump
    :param filename: The file to dump in
    :return: Nothing
    """
    file = open(filename, 'w')
    json.dump(object, file, default=json_default)
    file.close()


def retrieve_actors_from_json(filename):
    """
    Utility function to rebuild the actors dictionary from the given json file.
    :param filename: The json file to rebuild from.
    :return: A Dictionary (name of actor --> Actor Node)
    """
    file = open(filename, 'r')
    decoded_json = json.load(file)
    file.close()
    actors = []
    for actor in decoded_json:
        new_actor = Actor(actor['name'], actor['age'])
        new_actor.movies_starred_in = actor['movies_starred_in']
        new_actor.edges = actor['edges']
        new_actor.edge_weights = actor['edge_weights']
        actors.append(new_actor)
    actors = {node.name: node for node in actors}  # Convert to Dictionary
    return actors


def retrieve_movies_from_json(filename):
    """
    Utility function to rebuild the movies dictionary from the given json file.
    :param filename: The json file to rebuild from.
    :return: A Dictionary (name of movie --> Movie Node)
    """
    file = open(filename, 'r')
    decoded_json = json.load(file)
    file.close()
    movies = []
    for movie in decoded_json:
        new_movie = Movie(movie['name'], movie['year_released'], movie['gross_value'])
        new_movie.actors = movie['actors']
        new_movie.edges = movie['edges']
        new_movie.edge_weights = movie['edge_weights']
        movies.append(new_movie)
    movies = {node.name: node for node in movies}  # Convert to Dictionary
    return movies


def __main__():
    """
    Main function to execute the scraping, store the data to a JSON file and form a graph
    from the scraped data.
    :return: Nothing.
    """
    logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)  # Set up logging

    ACTOR_QUEUE.append(('Morgan Freeman', START))  # Add the starting node
    actors_scraped = 0  # Count of actors scrapped so far.
    movies_scraped = 0  # Count of movies scrapped so far.

    # Do the scraping
    while actors_scraped < ACTORS_LIMIT or movies_scraped < MOVIES_LIMIT:

        if len(ACTOR_QUEUE) > len(MOVIE_QUEUE) or (movies_scraped > MOVIES_LIMIT):

            actor_name, actor_link = ACTOR_QUEUE.pop(0)
            logging.info("Calling scrape_actor_page for {} at {}".format(actor_name, actor_link))
            actor_details, movies_to_add = scrape_actor_page(actor_name, WIKIPEDIA_URL+actor_link)
            if actor_details is not None:
                logging.debug("Adding {} to the ACTORS list.".format(actor_details.name))
                ACTORS[actor_details.name] = actor_details
                actors_scraped += (1 if len(actor_details.movies_starred_in) > 0 else 0)
            for movie_name, movie_link in movies_to_add.items():
                if (movie_name, movie_link) not in MOVIE_QUEUE and movie_name not in MOVIES:
                    logging.debug("Adding {} with link {} to the MOVIE_QUEUE".format(movie_name, movie_link))
                    MOVIE_QUEUE.append((movie_name, movie_link))

        else:

            movie_name, movie_link = MOVIE_QUEUE.pop(0)
            logging.info("Calling scrape_movie_page for {} at {}".format(movie_name, movie_link))
            movie_details, actors_to_add = scrape_movie_page(movie_name, WIKIPEDIA_URL+movie_link)
            if movie_details is not None:
                logging.debug("Adding {} to the MOVIES list.".format(movie_details.name))
                MOVIES[movie_details.name] = movie_details
                movies_scraped += (1 if len(movie_details.actors) > 0 else 0)
            for actor_name, actor_link in actors_to_add.items():
                if (actor_name, actor_link) not in ACTOR_QUEUE and actor_name not in ACTORS:
                    logging.debug("Adding {} with link {} to the ACTOR_QUEUE".format(actor_name, actor_link))
                    ACTOR_QUEUE.append((actor_name, actor_link))

        sleep(SLEEP_TIME)  # To avoid getting banned and overloading the web servers

        # Dump the scraped data as json files
        dump_into_json(list(ACTORS.values()), 'actors.json')
        dump_into_json(list(MOVIES.values()), 'movies.json')

        # Make the graph from the scraped data
        # actors, movies = make_graph(ACTORS, MOVIES)
        # graph = list(actors.values()).copy()
        # graph.extend(list(movies.values()).copy())
        # # Store it as json
        # dump_graph_as_json(graph)


if __name__ == '__main__':
    start_time = time()
    __main__()
    print("---%s seconds---" % (time() - start_time))