"""
Classes used for converting data retreived from API calls into database compatible classes
"""

from tmdbv3api import Movie
from tmdbv3api import TMDb
from tmdbv3api import TV

import database as database


API_KEY = "bc449fa32c4ebeda2a186af9137b58ec"  # Request a new one here: https://www.themoviedb.org/settings/api
CAST_AMOUNT = 3  # The amount of cast members you want to retrieve from the API
SIMILAR_AMOUNT = 8  # The amount of similar items that will be retrieved


# Data class for movie search results
class MovieSearchResult:
    def __init__(self):
        self.movie: database.Movie = None
        self.director: database.Contributor = None
        self.cast: [database.Contributor] = []


# Data class for the show search results
class TvShowSearchResult:
    def __init__(self):
        self.tvshow: database.TvShow = None
        self.episodes: [database.Episode] = []
        self.director: database.Contributor = None
        self.cast: [database.Contributor] = []


# Class to do all API request to
# Some kind of personal API wrapper of the tmdbv3 API wrapper
class Tmdbapi:
    tmdb = TMDb()
    tmdb.api_key = API_KEY

    def __init__(self):
        self.movie = Movie()
        self.tv = TV()

    # Movies

    # Search for a movie and find the movie's data, its director and its cast
    # Put all of that in a data holding object
    # The data is NOT LINKED TO EACH OTHER
    # This linking has to be done elsewhere by checking the database
    # For example:
    #           the movie's director property will be None, the director's id will be None, the cast's id's will be None
    # Their names need to be checked in the database first to make sure not to add them twice

    # Convert tmdbv3 API data into our own MovieSearchResult
    def tmdb_to_movie(self, moviedata) -> MovieSearchResult:
        movie = database.Movie()
        movie.tmdbId = moviedata.id
        movie.title = moviedata.title
        movie.description = moviedata.overview

        movie_credits = self.movie.credits(moviedata.id).entries

        movie.director = None

        movie_details = self.movie.details(moviedata.id).entries
        runtime = None
        genre = None

        if movie_details is not None:
            if "runtime" in movie_details.keys():
                runtime = movie_details["runtime"]
            else:
                runtime = 0
                
            if "genres" in movie_details.keys():
                genres = movie_details["genres"]
            else:
                genres = None
                
            if genres is not None and len(genres) > 0:
                genre = genres[0]["name"]
            else:
                genre = "Unknown"

        movie.runtime = runtime
        movie.genre = genre

        if hasattr(moviedata, 'release_date') and len(moviedata.release_date) != 0:
            movie.releaseYear = int(moviedata.release_date[0:4])
        else:
            movie.releaseYear = 0
        movie.avgRating = moviedata.vote_average

        # Director

        director = None
        director_name = None
        crew = []

        if "crew" in movie_credits.keys():
            crew = movie_credits["crew"]
            
        for person in crew:
            if person["job"] == "Director":
                director_name = person["name"]
                break

        if director_name is not None:
            director = database.Contributor()
            director.name = director_name

        # Cast

        cast = []
        actors = []
        if "cast" in movie_credits.keys():
            actors = movie_credits["cast"]

        for actor in actors[0:CAST_AMOUNT]:
            cast_member = database.Contributor()
            cast_member.name = actor["name"]
            cast.append(cast_member)

        output = MovieSearchResult()
        output.movie = movie
        output.director = director
        output.cast = cast

        return output

    # Search for a movie by title and duration
    def search_movie(self, query: str, duration: int) -> MovieSearchResult:
        search = self.movie.search(query)

        output = None

        for movie_data in search:
            movie = self.tmdb_to_movie(movie_data)
            if output is None:
                output = movie
            #elif abs(movie.movie.runtime - duration) < abs(output.movie.runtime - duration):
                #output = movie

        return output

    # Search multiple movies by title
    def search_movies(self, query: str, max_movies: int) -> [MovieSearchResult]:
        search = self.movie.search(query)

        output = []

        for movie_data in search:
            if len(output) >= max_movies:
                break

            movie = self.tmdb_to_movie(movie_data)
            output.append(movie)

        return output

    # "Download" a movie thumbnail
    def get_poster_movie(self, tmdb_id: int) -> str:
        movie_result = self.movie.details(tmdb_id)
        poster_path = movie_result.poster_path

        if poster_path is None:
            return None

        return "https://image.tmdb.org/t/p/w500" + poster_path

    # Get similar tmdb movies
    def get_similar_tmdb_movies(self, tmdb_id: int) -> [MovieSearchResult]:
        output = []
        for moviedata in self.movie.similar(tmdb_id):
            output.append(self.tmdb_to_movie(moviedata))
            if len(output) == SIMILAR_AMOUNT:
                break
        return output

    # TV shows

    # Convert tmdbv3 API data into our own TvShowSearchResult
    def tmdb_to_tvshow(self, tvshowdata) -> TvShowSearchResult:
        tvshow = database.TvShow()
        tvshow.title = tvshowdata.name
        tvshow.tmdbId = tvshowdata.id
        tvshow.description = tvshowdata.overview

        tvshow.director = None

        tvshow_details = self.tv.details(tvshowdata.id).entries
        runtime = 0
        genre = None

        if tvshow_details is not None:
            if "episode_run_time" in tvshow_details.keys():
                runtimes = tvshow_details["episode_run_time"]
            else:
                runtimes = None

            if runtimes is not None and len(runtimes) != 0:
                runtime = runtimes[0]

            if "genres" in tvshow_details.keys():
                genres = tvshow_details["genres"]
            else:
                genres = None

            if genres is not None and len(genres) > 0:
                genre = genres[0]["name"]
            else:
				genre = "Unknown"

        tvshow.runtime = runtime
        tvshow.genre = genre

        if hasattr(tvshowdata, 'first_air_date') and len(tvshowdata.first_air_date) != 0:
            tvshow.releaseYear = int(tvshowdata.first_air_date[0:4])
        else:
            tvshow.releaseYear = 0

        tvshow.avgRating = tvshowdata.vote_average

        # Director

        director = None
        
        if "created_by" in tvshow_details.keys():
            created_by = tvshow_details["created_by"]
        else:
            created_by = None

        if created_by is not None and len(created_by) != 0:
            director = database.Contributor()
            director.name = created_by[0]["name"]

        # Cast

        cast = []
        if "credits" in tvshow_details.keys():
            if "cast" in tvshow_details["credits"].keys():
                actors = tvshow_details["credits"]["cast"]
        else:
            actors = []

        for actor in actors[0:CAST_AMOUNT]:
            cast_member = database.Contributor()
            cast_member.name = actor["name"]
            cast.append(cast_member)

        # Episodes

        episodes = []

        if "seasons" in tvshow_details.keys():
            seasons_data = tvshow_details["seasons"]
            for season_data in seasons_data:
                season_nr = season_data["season_number"]
                for episode_nr in range(1, season_data["episode_count"] + 1):
                    episode = database.Episode()
                    episode.tmdbId = None
                    episode.season = season_nr
                    episode.episode = episode_nr
                    episodes.append(episode)

        output = TvShowSearchResult()
        output.tvshow = tvshow
        output.episodes = episodes
        output.director = director
        output.cast = cast

        return output

    # Search for a tv show via the API and turn the found data into a database supported object
    def search_tvshow(self, query: str, duration: int) -> TvShowSearchResult:
        search = self.tv.search(query)

        output = None

        for tvshow_data in search:
            tvshow = self.tmdb_to_tvshow(tvshow_data)
            if output is None:
                output = tvshow
            #elif abs(tvshow.tvshow.runtime - duration) < abs(output.tvshow.runtime - duration):
                #output = tvshow

        return output

    # Search for a tv show via the API and turn the found data into a database supported object
    def search_tvshows(self, query: str, max_tvshows: int) -> [TvShowSearchResult]:
        search = self.tv.search(query)

        output = []

        for tvshowdata in search:
            if len(output) >= max_tvshows:
                break

            tvshow = self.tmdb_to_tvshow(tvshowdata)
            output.append(tvshow)

        return output

    # "Download" a tv show thumbnail
    def get_poster_tv(self, tmdb_id: int) -> str:
        tv_result = self.tv.details(tmdb_id)
        poster_path = tv_result.poster_path

        if poster_path is None:
            return None

        return "https://image.tmdb.org/t/p/w500" + poster_path

    # Get the similar items of a tv show
    def get_similar_tmdb_tvshows(self, tmdb_id: int) -> [TvShowSearchResult]:
        output = []
        for tvshowdata in self.tv.similar(tmdb_id):
            output.append(self.tmdb_to_tvshow(tvshowdata))
            if len(output) == SIMILAR_AMOUNT:
                break
        return output
