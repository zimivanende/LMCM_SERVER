import mysql.connector as mariadb
from singleton import Singleton
import random
import string


DB_USER = "root"
DB_PASS = "password"
DB_NAME= "lmcm"

LICENSE_KEY_SECTION_LENGHT = 5
LICENSE_KEY_SECTIONS = 5

CLIENT_ID_LENGHT = 16
        

class Movie:
    @staticmethod
    def from_dictionary(dic: {}):
        movie = Movie()

        for i, v in dic.items():
            setattr(movie, i, v)

        return movie

    def __init__(self):
        self.itemId = None
        self.tmdbId = None
        self.title = None
        self.description = None
        self.director = None
        self.runtime = None
        self.genre = None
        self.releaseYear = None
        self.avgRating = None
        self.posterURL = None


class Episode:
    @staticmethod
    def from_dictionary(dic: {}):
        episode = Episode()

        for i, v in dic.items():
            setattr(episode, i, v)

        return episode

    def __init__(self):
        self.itemId = None
        self.parentId = None
        self.episode = None
        self.season = None


class TvShow:
    @staticmethod
    def from_dictionary(dic: {}):
        tvshow = TvShow()

        for i, v in dic.items():
            setattr(tvshow, i, v)

        return tvshow

    def __init__(self):
        self.itemId = None
        self.tmdbId = None
        self.title = None
        self.description = None
        self.director = None
        self.runtime = None
        self.genre = None
        self.releaseYear = None
        self.avgRating = None
        self.posterURL = None


class Track:
    @staticmethod
    def from_dictionary(dic: {}):
        track = Track()

        for i, v in dic.items():
            setattr(track, i, v)

        return track

    def __init__(self):
        self.itemId = None
        self.parentId = None
        self.title = None


class Album:
    @staticmethod
    def from_dictionary(dic: {}):
        album = Album()

        for i, v in dic.items():
            setattr(album, i, v)

        return album

    def __init__(self):
        self.itemId = None
        self.title = None
        self.artist = None
        self.genre = None
        self.releaseYear = None
        self.avgRating = None
        self.posterURL = None


class Contributor:
    @staticmethod
    def from_dictionary(dic: {}):
        contributor = Contributor()

        for i, v in dic.items():
            setattr(contributor, i, v)

        return contributor

    def __init__(self):
        self.id = None
        self.name = None


class StarsIn:
    @staticmethod
    def from_dictionary(dic: {}):
        starsin = StarsIn()

        for i, v in dic.items():
            setattr(starsin, i, v)

        return starsin

    def __init__(self):
        self.id = None
        self.contributorId = None
        self.itemId = None


class Similar:
    @staticmethod
    def from_dictionary(dic: {}):
        similar = Similar()

        for i, v in dic.items():
            setattr(similar, i, v)

        return similar

    def __init__(self):
        self.itemId = None
        self.otherItemId1 = None
        self.otherItemId2 = None
        self.otherItemId3 = None
        self.otherItemId4 = None
        self.otherItemId5 = None
        self.otherItemId6 = None
        self.otherItemId7 = None
        self.otherItemId8 = None


class Rating:
    @staticmethod
    def from_dictionary(dic: {}):
        rating = Rating()

        for i, v in dic.items():
            setattr(rating, i, v)

        return rating

    def __init__(self):
        self.id = None
        self.clientId = None
        self.userId = None
        self.itemId = None
        self.rating = None


class Database(metaclass=Singleton):
    def __init__(self):
        try:
            self.conn = mariadb.connect(user=DB_USER, password=DB_PASS, database=DB_NAME)
        except Exception as e:
            print("Could not connect to database to create tables: {}".format(str(e.args)))
            exit()

    # "destructor": close the database connection
    def __del__(self):
        self.conn.close()

    # Generate a new unique id for a generic item
    def get_new_item_id(self) -> int:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        cursor.execute("SELECT MAX(itemId) FROM Movies")
        movie_max = (cursor.fetchone())["MAX(itemId)"]

        cursor.execute("SELECT MAX(itemId) FROM TvShows")
        tvshow_max = (cursor.fetchone())["MAX(itemId)"]

        cursor.execute("SELECT MAX(itemId) FROM Episodes")
        episodes_max = (cursor.fetchone())["MAX(itemId)"]

        cursor.execute("SELECT MAX(itemId) FROM Albums")
        albums_max = (cursor.fetchone())["MAX(itemId)"]

        cursor.execute("SELECT MAX(itemId) FROM Tracks")
        tracks_max = (cursor.fetchone())["MAX(itemId)"]

        if movie_max is None:
            movie_max = 0
        if tvshow_max is None:
            tvshow_max = 0
        if episodes_max is None:
            episodes_max = 0
        if albums_max is None:
            albums_max = 0
        if tracks_max is None:
            tracks_max = 0

        ids = [movie_max, tvshow_max, episodes_max, albums_max, tracks_max]

        new_id = max(ids)

        return new_id + 1

    # Movies

    # Return a certain movie by item id
    def get_movie_by_item_id(self, item_id: int) -> Movie:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        params = (item_id,)
        cursor.execute("SELECT * FROM Movies WHERE itemId = %s", params)
        result = cursor.fetchone()

        if result is not None:
            return Movie.from_dictionary(result)
        else:
            return None

    # Return a certain movie by tmdb id
    def get_movie_by_tmdb_id(self, tmdb_id: int) -> Movie:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        params = (tmdb_id,)
        cursor.execute("SELECT * FROM Movies WHERE tmdbId = %s", params)
        result = cursor.fetchone()

        if result is not None:
            return Movie.from_dictionary(result)
        else:
            return None

    def get_movie_by_title(self, title: str) -> Movie:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)
        
        params = (title,)
        cursor.execute("SELECT * FROM Movies WHERE title = %s", params)
        result = cursor.fetchone()

        if result is not None:
            return Movie.from_dictionary(result)
        else:
            return None

    # Add a certain movie object to the database
    def add_movie(self, movie: Movie) -> None:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        params = (movie.itemId, movie.tmdbId, movie.title, movie.description, movie.director, movie.runtime, movie.genre, movie.releaseYear, movie.avgRating, movie.posterURL)
        cursor.execute("INSERT INTO Movies VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", params)
        self.conn.commit()

    # Returns all existing movie release years
    def get_movie_release_years(self) -> [int]:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        cursor.execute("SELECT DISTINCT releaseYear FROM Movies ORDER BY releaseYear")
        dicts = cursor.fetchall()

        result = [entry["releaseYear"] for entry in dicts]

        return result

    # Episodes

    # Return a certain episode object by item id
    def get_episode_by_item_id(self, item_id: int) -> Episode:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        params = (item_id,)
        cursor.execute("SELECT * FROM Episodes WHERE itemId = %s", params)
        result = cursor.fetchone()

        if result is not None:
            return Episode.from_dictionary(result)
        else:
            return None

    # Return a certain episode object by item id
    def get_episode_by_season_and_episode(self, parent_id: int, season: int, episode: int) -> Episode:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        params = (parent_id, season, episode)
        cursor.execute("SELECT * FROM Episodes WHERE parentId = %s AND season = %s AND episode = %s", params)
        result = cursor.fetchone()

        if result is not None:
            return Episode.from_dictionary(result)
        else:
            return None

    # Add a certain episode object to the database
    def add_episode(self, episode: Episode) -> None:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        params = (episode.itemId, episode.parentId, episode.episode, episode.season)
        cursor.execute("INSERT INTO Episodes VALUES (%s, %s, %s, %s)", params)
        self.conn.commit()

    # Tv Shows

    # Return a certain tvshow object by item id
    def get_tvshow_by_item_id(self, item_id: int) -> TvShow:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        params = (item_id,)
        cursor.execute("SELECT * FROM TvShows WHERE itemId = %s", params)
        result = cursor.fetchone()

        if result is not None:
            return TvShow.from_dictionary(result)
        else:
            return None

    # Return a certain episode object by tmdb id
    def get_tvshow_by_tmdb_id(self, tmdbid: int) -> TvShow:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        params = (tmdbid,)
        cursor.execute("SELECT * FROM TvShows WHERE tmdbId = %s", params)
        result = cursor.fetchone()

        if result is not None:
            return TvShow.from_dictionary(result)
        else:
            return None

    # Add a certain tvshow object to the database
    def add_tvshow(self, tvshow: TvShow) -> None:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        params = (tvshow.itemId, tvshow.tmdbId, tvshow.title, tvshow.description, tvshow.director, tvshow.runtime, tvshow.genre, tvshow.releaseYear, tvshow.avgRating, tvshow.posterURL)
        cursor.execute("INSERT INTO TvShows VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", params)
        self.conn.commit()

    # Returns all existing tvshow release years
    def get_tvshow_release_years(self) -> [int]:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        cursor.execute("SELECT DISTINCT releaseYear FROM TvShows ORDER BY releaseYear")
        dicts = cursor.fetchall()

        result = [entry["releaseYear"] for entry in dicts]

        return result

    # Tracks

    # Return a certain track object by item id
    def get_track_by_item_id(self, item_id: int) -> Track:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        params = (item_id,)
        cursor.execute("SELECT * FROM Tracks WHERE itemId = %s", params)
        result = cursor.fetchone()

        if result is not None:
            return Track.from_dictionary(result)
        else:
            return None

    def get_tracks_of_item_id(self, item_id: int) -> [Track]:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        params = (item_id,)
        cursor.execute("SELECT * FROM Tracks WHERE parentId = %s", params)
        result = cursor.fetchall()

        tracks = [Track.from_dictionary(r) for r in result]

        return tracks

        # Add a certain track object to the database

    def add_track(self, track: Track) -> None:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        params = (track.itemId, track.parentId, track.title)
        cursor.execute("INSERT INTO Tracks VALUES (%s, %s, %s)", params)
        self.conn.commit()

    # Albums

    # Return a certain album object by item id
    def get_album_by_item_id(self, item_id: int) -> Album:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        params = (item_id,)
        cursor.execute("SELECT * FROM Albums WHERE itemId = %s", params)
        result = cursor.fetchone()

        if result is not None:
            return Album.from_dictionary(result)
        else:
            return None

    # Add a certain album object to the database
    def add_album(self, album: Album) -> None:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        params = (album.itemId, album.title, album.artist, album.genre, album.releaseYear, album.avgRating, album.posterURL)
        cursor.execute("INSERT INTO Albums VALUES (%s, %s, %s, %s, %s, %s, %s)", params)
        self.conn.commit()

    # Returns all existing movie release years
    def get_album_release_years(self) -> [int]:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        cursor.execute("SELECT DISTINCT releaseYear FROM Albums ORDER BY releaseYear")
        dicts = cursor.fetchall()

        result = [entry["releaseYear"] for entry in dicts]

        return result

    # StarsIn & Contributors

    # Return a list containing contributors linked to a certain file
    # Concrete: get all actors that worked on a movie
    def get_contributors_of_item_id(self, item_id: int) -> [Contributor]:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        params = (item_id,)
        cursor.execute("SELECT Contributors.id, Contributors.name "
                                   "FROM Contributors, StarsIn "
                                   "WHERE StarsIn.contributorId = Contributors.id AND StarsIn.itemId = %s", params)
        result = cursor.fetchall()

        contributors = [Contributor.from_dictionary(r) for r in result]

        return contributors

    # Return a certain contributor object by id
    def get_contributor_by_id(self, id: int) -> Contributor:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        params = (id,)
        cursor.execute("SELECT * FROM Contributors WHERE id = %s", params)
        result = cursor.fetchone()

        if result is not None:
            return Contributor.from_dictionary(result)
        else:
            return None

    # Return all contributors in the database
    def get_contributors(self) -> [Contributor]:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        cursor.execute("SELECT * FROM Contributors")
        result = cursor.fetchall()

        contributors = [Contributor.from_dictionary(r) for r in result]

        return contributors

    # Add a certain contributor object to the database
    def add_contributor(self, contributor: Contributor) -> None:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        params = (contributor.name,)
        cursor.execute("INSERT INTO Contributors(name) VALUES (%s)", params)
        self.conn.commit()

    # Return a certain contributor object by name
    def get_contributor_by_name(self, name: str) -> Contributor:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        params = (name,)
        cursor.execute("SELECT * FROM Contributors WHERE name = %s", params)
        result = cursor.fetchone()

        if result is not None:
            return Contributor.from_dictionary(result)
        else:
            return None

    def add_starsin(self, stars_in: StarsIn) -> None:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        params = (stars_in.contributorId, stars_in.itemId)
        cursor.execute("INSERT INTO StarsIn(contributorId, itemId) VALUES (%s, %s)", params)
        self.conn.commit()

    # Similar

    # Add a certain similar object to the database
    def add_similar(self, similar: Similar) -> None:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        params = (similar.itemId, similar.otherItemId1, similar.otherItemId2, similar.otherItemId3, similar.otherItemId4, similar.otherItemId5, similar.otherItemId6, similar.otherItemId7, similar.otherItemId8)
        cursor.execute("INSERT INTO Similar VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", params)
        self.conn.commit()

    # Get the 8 similar items to a certain item
    def get_similar_of_item_id(self, item_id: int) -> []:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        params = (item_id, )
        cursor.execute("SELECT * FROM Similar WHERE itemId = %s", params)
        result = cursor.fetchone()

        if result is None:
            return []

        similar = Similar.from_dictionary(result)
        print(similar.__dict__)

        output = []

        for i in ["otherItemId1", "otherItemId2", "otherItemId3", "otherItemId4", "otherItemId5", "otherItemId6", "otherItemId7", "otherItemId8"]:
            output.append(self.get_item_by_item_id(similar.__dict__[i]))

        return output

    # Get all info of a certain top level item
    # This means, get the item that has item id
    def get_item_by_item_id(self, item_id: int):
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        # Check if it's a movie
        params = (item_id,)
        cursor.execute("SELECT * FROM Movies WHERE itemId = %s", params)
        result = cursor.fetchone()

        if result is not None:
            return Movie.from_dictionary(result)

        # Check if it's a tvshow
        params = (item_id,)
        cursor.execute("SELECT * FROM TvShows WHERE itemId = %s", params)
        result = cursor.fetchone()

        if result is not None:
            return TvShow.from_dictionary(result)

        # Check if it's an episode
        params = (item_id,)
        cursor.execute("SELECT * FROM Episodes WHERE itemId = %s", params)
        result = cursor.fetchone()

        if result is not None:
            return Episode.from_dictionary(result)

        # Check if it's a album
        params = (item_id,)
        cursor.execute("SELECT * FROM Albums WHERE itemId = %s", params)
        result = cursor.fetchone()

        if result is not None:
            return Album.from_dictionary(result)

        # Check if it's a track
        params = (item_id,)
        cursor.execute("SELECT * FROM Tracks WHERE itemId = %s", params)
        result = cursor.fetchone()

        if result is not None:
            return Track.from_dictionary(result)

        return None

    # Search for a movie by substring
    def search_movie(self, search: str) -> Movie:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        search = "%" + search + "%"  # conversion necessary for SQL LIKE statement

        # Search in movie title
        params = (search,)
        cursor.execute("SELECT * FROM Movies WHERE lower(title) LIKE lower(%s)", params)
        result = cursor.fetchone()

        if result is not None:
            return Movie.from_dictionary(result)

        return None

    # Search for a movie by substring
    def search_movies(self, search: str) -> [Movie]:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        search = "%" + search + "%"  # conversion necessary for SQL LIKE statement

        # Search in movie title
        params = (search,)
        cursor.execute("SELECT * FROM Movies WHERE lower(title) LIKE lower(%s)", params)
        result = cursor.fetchall()

        movies = [Movie.from_dictionary(r) for r in result]

        return movies

    # Search for a tv show by substring
    def search_tvshow(self, search: str) -> TvShow:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        search = "%" + search + "%"  # conversion necessary for SQL LIKE statement

        # Search in tv show title
        params = (search,)
        cursor.execute("SELECT * FROM TvShows WHERE lower(title) LIKE lower(%s)", params)
        result = cursor.fetchone()

        if result is not None:
            return TvShow.from_dictionary(result)

        return None

    # Search for a tv show by substring
    def search_tvshows(self, search: str) -> [TvShow]:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        search = "%" + search + "%"  # conversion necessary for SQL LIKE statement

        # Search in tv show title
        params = (search,)
        cursor.execute("SELECT * FROM TvShows WHERE lower(title) LIKE lower(%s)", params)
        result = cursor.fetchall()

        tvshows = [TvShow.from_dictionary(r) for r in result]

        return tvshows

    # Search for a track by substring
    def search_track(self, search: str) -> Track:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        search = "%" + search + "%"  # conversion necessary for SQL LIKE statement

        # Search in track title
        params = (search,)
        cursor.execute("SELECT * FROM Tracks WHERE lower(title) LIKE lower(%s)", params)
        result = cursor.fetchone()

        if result is not None:
            return Track.from_dictionary(result)
        else:
            return None

    # Search for an album by substring
    def search_album(self, search: str) -> Album:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        search = "%" + search + "%"  # conversion necessary for SQL LIKE statement

        # Search in movie title
        params = (search,)
        cursor.execute("SELECT * FROM Albums WHERE lower(title) LIKE lower(%s)", params)
        result = cursor.fetchone()

        if result is not None:
            return Album.from_dictionary(result)

        return None

    # Search for an album by substring
    def search_albums(self, search: str) -> [Album]:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        search = "%" + search + "%"  # conversion necessary for SQL LIKE statement

        # Search in movie title
        params = (search,)
        cursor.execute("SELECT * FROM Albums WHERE lower(title) LIKE lower(%s)", params)
        result = cursor.fetchall()

        albums = [Album.from_dictionary(r) for r in result]

        return albums

    # Return a list containing episodes linked to a certain item
    def get_episodes_of_item_id(self, item_id: int) -> [Episode]:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        params = (item_id,)
        cursor.execute("SELECT * FROM Episodes WHERE parentId = %s", params)
        result = cursor.fetchall()

        episodes = [Episode.from_dictionary(r) for r in result]

        return episodes

    # Return the license key data of a license key
    def get_licensekey_data(self, license_key: str) -> {}:
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        params = (license_key,)
        cursor.execute("SELECT * FROM Licenses WHERE licenseKey = %s", params)
        result = cursor.fetchone()

        return result

    # Get the data of a license key by license id
    def get_licensekey_data_by_id(self, license_id: int) -> {}:
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        params = (license_id,)
        cursor.execute("SELECT * FROM Licenses WHERE licenseId = %s", params)
        result = cursor.fetchone()

        return result

    def update_max_clients_licensekey_by_id(self, license_id: int, new_max_clients: int):
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        params = (new_max_clients, license_id,)
        cursor.execute("UPDATE Licenses SET maxClients = %s WHERE licenseId = %s", params)
        self.conn.commit()


    # Update the used clients value
    def update_used_clients(self, license_id: int, new_used_clients: int):
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        params = (new_used_clients, license_id,)
        cursor.execute("UPDATE Licenses SET usedClients = %s WHERE licenseId = %s", params)
        self.conn.commit()

    # Check if a client id exists
    def check_client_id(self, client_id: str) -> bool:
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        params = (client_id,)
        cursor.execute("SELECT clientId FROM Clients WHERE clientId = %s", params)
        result = cursor.fetchone()

        return result is not None

    # Return a dictionary with client data
    def get_client_data(self, client_id: str) -> {}:
        cursor = self.conn.cursor(dictionary=True, buffered=True)

        params = (client_id,)
        cursor.execute("SELECT * FROM Clients WHERE clientId = %s", params)
        result = cursor.fetchone()

        return result

    # Remove a client from the database by client id
    def remove_client_id(self, client_id: str):
        cursor = self.conn.cursor(dictionary=True, buffered=True)
        params = (client_id,)
        cursor.execute("DELETE FROM Clients WHERE clientId = %s", params)
        self.conn.commit()

    # Add a new client to the database
    def add_new_client_id(self, license_id: int) -> str:
        client_id = self.generate_client_id()
        while self.check_client_id(client_id):
            client_id = self.generate_client_id()

        cursor = self.conn.cursor(dictionary=True, buffered=True)
        params = (client_id, license_id)
        cursor.execute("INSERT INTO Clients (clientId, licenseId) VALUES (%s, %s)", params)
        self.conn.commit()

        return client_id

    # Generate a new client id
    def generate_client_id(self) -> str:
        seed = string.ascii_letters + string.digits
        client_id = ''.join((random.choice(seed) for i in range(CLIENT_ID_LENGHT)))

        return client_id

    # Generate a new license key
    def generate_license_key(self) -> str:
        seed = string.ascii_uppercase + string.digits
        license_key = ""
        for i in range(LICENSE_KEY_SECTIONS):
            if len(license_key) != 0:
                license_key += "-"
            license_key += ''.join((random.choice(seed) for i in range(LICENSE_KEY_SECTION_LENGHT)))

        return license_key

    # Add a new license key to the database
    def add_new_license_key(self, max_clients) -> str:
        license_key = self.generate_license_key()
        while self.get_licensekey_data(license_key) is not None:
            license_key = self.generate_license_key()

        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)
        params = (license_key, 0, max_clients)
        cursor.execute("INSERT INTO Licenses (licenseKey, usedClients, maxClients) VALUES (%s, %s, %s)", params)
        self.conn.commit()

        return license_key

    # Ratings

    # Add a certain movie object to the database
    def add_rating(self, rating: Rating) -> None:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)
        params = (rating.clientId, rating.userId, rating.itemId, rating.rating)
        cursor.execute("INSERT INTO Ratings(clientId, userId, itemId, rating) VALUES(%s, %s, %s, %s)", params)
        self.conn.commit()

    # Get ratings of client and user id
    def get_ratings_of_client_user(self, client_id: str, user_id: int) -> [Rating]:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)
        params = (client_id, user_id)
        cursor.execute("SELECT * FROM Ratings WHERE clientId = %s AND userId = %s ORDER BY rating DESC", params)
        result = cursor.fetchall()

        ratings = [Rating.from_dictionary(r) for r in result]

        return ratings

    # Get all ratings in the database
    def get_ratings(self) -> [Rating]:
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)
        cursor.execute("SELECT * FROM Ratings")
        result = cursor.fetchall()

        ratings = [Rating.from_dictionary(r) for r in result]

        return ratings

    # Remove all ratings of a client's user
    def clear_client_user_ratings(self, client_id: str, user_id: int):
        # create new cursor
        cursor = self.conn.cursor(dictionary=True, buffered=True)
        params = (client_id, user_id)
        cursor.execute("DELETE FROM Ratings WHERE clientId = %s AND userId = %s", params)
        self.conn.commit()
