from tmdbv import Tmdbapi
from database import Database, Movie, TvShow, Episode, Album, Track, StarsIn, Similar, Contributor, Rating


class MetaFinder:
    def __init__(self):
        pass

    def search_movie(self, title: str, duration: int) -> Movie:
        # Search in database
        movie = Database().search_movie(title)

        if movie is not None:
            return movie

        # Search via APIs
        api = Tmdbapi()
        search_result = api.search_movie(title, duration)

        if search_result is not None and search_result.movie is not None:
            # Double check if the data is already in the database
            movie = Database().get_movie_by_tmdb_id(search_result.movie.tmdbId)

            if movie is not None:
                return movie

            movie = search_result.movie
            director = search_result.director
            cast = search_result.cast

            poster_url = api.get_poster_movie(movie.tmdbId)

            movie = self.add_new_movie_to_database(movie, director, cast, poster_url)

            return movie
        else:
            return None

    def search_movies(self, title: str, max_movies: int) -> [Movie]:
        # Search in database
        movies = Database().search_movies(title)

        if len(movies) >= max_movies:
            movies = movies[:max_movies]
            return movies

        # Search via APIs
        api = Tmdbapi()
        search_results = api.search_movies(title, max_movies - len(movies))

        for search_result in search_results:
            # Double check if the data is already in the database
            movie = Database().get_movie_by_tmdb_id(search_result.movie.tmdbId)

            if movie is not None:
                if movie.itemId not in [m.itemId for m in movies]:
                    movies.append(movie)
                else:
                    continue

            movie = search_result.movie
            director = search_result.director
            cast = search_result.cast

            poster_url = api.get_poster_movie(movie.tmdbId)

            movie = self.add_new_movie_to_database(movie, director, cast, poster_url)

            movies.append(movie)

        return movies

    def get_all_contributors(self, item_id: int, director_id: int) -> [Contributor]:
        contributors = Database().get_contributors_of_item_id(item_id)
        if director_id is not None:
            contributors.append(Database().get_contributor_by_id(director_id))
        return contributors

    def get_director_or_artist(self, contributor_id: int) -> Contributor:
        return Database().get_contributor_by_id(contributor_id)

    # Adds a movie with all its info to the database
    def add_new_movie_to_database(self, movie: Movie, director: Contributor, cast: [Contributor], poster_url: str) -> Movie:
        movie.itemId = Database().get_new_item_id()
        movie.posterURL = poster_url

        if director is not None:
            if Database().get_contributor_by_name(director.name) is None:
                Database().add_contributor(director)

            director = Database().get_contributor_by_name(director.name)

            movie.director = director.id
        else:
            movie.director = None

        for cast_member in cast:
            if Database().get_contributor_by_name(cast_member.name) is None:
                Database().add_contributor(cast_member)

            cast_member = Database().get_contributor_by_name(cast_member.name)

            starsin = StarsIn()
            starsin.itemId = movie.itemId
            starsin.contributorId = cast_member.id

            Database().add_starsin(starsin)

        Database().add_movie(movie)

        # Init movie in ratings
        db_rating = Rating()
        db_rating.clientId = "server"
        db_rating.userId = 0
        db_rating.itemId = movie.itemId
        db_rating.rating = 0.0

        Database().add_rating(db_rating)

        return movie

    def get_similar_movies(self, item_id: int) -> [Movie]:
        requested_movie = Database().get_movie_by_item_id(item_id)
        similar_movies = Database().get_similar_of_item_id(item_id)

        if len(similar_movies) == 0:
            api = Tmdbapi()
            api_movies = api.get_similar_tmdb_movies(requested_movie.tmdbId)
            dic = {"itemId": requested_movie.itemId}
            i = 1

            for api_movie in api_movies:
                # Movie already in database
                movie = Database().get_movie_by_tmdb_id(api_movie.movie.tmdbId)

                if movie is not None:
                    dic["otherItemId" + str(i)] = movie.itemId
                else:
                    search_result = api_movie

                    if search_result is None:
                        continue

                    movie = search_result.movie
                    director = search_result.director
                    cast = search_result.cast
                    poster_url = api.get_poster_movie(movie.tmdbId)

                    movie = self.add_new_movie_to_database(movie, director, cast, poster_url)
                    dic["otherItemId" + str(i)] = movie.itemId

                i += 1
                if i > 8:
                    break

            similar = Similar.from_dictionary(dic)
            Database().add_similar(similar)
            similar_movies = Database().get_similar_of_item_id(item_id)

        return similar_movies

    # TV Shows

    def search_tvshow(self, title: str, duration: int) -> TvShow:
        tvshow = Database().search_tvshow(title)

        if tvshow is not None:
            return tvshow

        api = Tmdbapi()
        search_result = api.search_tvshow(title, duration)

        if search_result is not None and search_result.tvshow is not None:
            # Double check if the data is already in the database
            tvshow = Database().get_tvshow_by_tmdb_id(search_result.tvshow.tmdbId)

            if tvshow is not None:
                return tvshow

            tvshow = search_result.tvshow
            episodes = search_result.episodes
            director = search_result.director
            cast = search_result.cast

            poster_url = api.get_poster_tv(tvshow.tmdbId)

            tvshow = self.add_new_tvshow_to_database(tvshow, episodes, director, cast, poster_url)

            return tvshow
        else:
            return None

    def search_tvshows(self, title: str, max_tvshows: int) -> [TvShow]:
        tvshows = Database().search_tvshows(title)

        if len(tvshows) >= max_tvshows:
            tvshows = tvshows[:max_tvshows]
            return tvshows

        api = Tmdbapi()
        search_results = api.search_tvshows(title, max_tvshows - len(tvshows))

        for search_result in search_results:
            # Double check if the data is already in the database
            tvshow = Database().get_tvshow_by_tmdb_id(search_result.tvshow.tmdbId)

            if tvshow is not None:
                if tvshow.itemId not in [t.itemId for t in tvshows]:
                    tvshows.append(tvshow)
                else:
                    continue

            tvshow = search_result.tvshow
            episodes = search_result.episodes
            director = search_result.director
            cast = search_result.cast

            poster_url = api.get_poster_tv(tvshow.tmdbId)

            tvshow = self.add_new_tvshow_to_database(tvshow, episodes, director, cast, poster_url)

            tvshows.append(tvshow)

        return tvshows

    def get_all_episodes(self, item_id: int) -> [Episode]:
        return Database().get_episodes_of_item_id(item_id)

    def add_new_tvshow_to_database(self, tvshow, episodes, director, cast, poster_url) -> TvShow:
        tvshow.itemId = Database().get_new_item_id()
        tvshow.posterURL = poster_url

        if director is not None:
            if Database().get_contributor_by_name(director.name) is None:
                Database().add_contributor(director)

            director = Database().get_contributor_by_name(director.name)

            tvshow.director = director.id
        else:
            tvshow.director = None

        for cast_member in cast:
            if Database().get_contributor_by_name(cast_member.name) is None:
                Database().add_contributor(cast_member)

            cast_member = Database().get_contributor_by_name(cast_member.name)

            starsin = StarsIn()
            starsin.itemId = tvshow.itemId
            starsin.contributorId = cast_member.id

            Database().add_starsin(starsin)

        for e in episodes:
            e.itemId = Database().get_new_item_id()
            e.parentId = tvshow.itemId
            Database().add_episode(e)

        Database().add_tvshow(tvshow)

        # Init tvshow in ratings
        db_rating = Rating()
        db_rating.clientId = "server"
        db_rating.userId = 0
        db_rating.itemId = tvshow.itemId
        db_rating.rating = 0.0

        Database().add_rating(db_rating)

        return tvshow

    def get_similar_tvshows(self, item_id: int) -> [TvShow]:
        requested_tvshow = Database().get_tvshow_by_item_id(item_id)
        similar_tvshows = Database().get_similar_of_item_id(item_id)

        if len(similar_tvshows) == 0:
            api = Tmdbapi()
            api_tvshows = api.get_similar_tmdb_tvshows(requested_tvshow.tmdbId)
            dic = {"itemId": requested_tvshow.itemId}
            i = 1

            for api_tvshow in api_tvshows:
                # tvshow already in database
                tvshow = Database().get_tvshow_by_tmdb_id(api_tvshow.tvshow.tmdbId)

                if tvshow is not None:
                    dic["otherItemId" + str(i)] = tvshow.itemId
                else:
                    search_result = api_tvshow

                    if search_result is None:
                        continue

                    tvshow = search_result.tvshow
                    episodes = search_result.episodes
                    director = search_result.director
                    cast = search_result.cast

                    poster_url = api.get_poster_tv(tvshow.tmdbId)

                    tvshow = self.add_new_tvshow_to_database(tvshow, episodes, director, cast, poster_url)
                    dic["otherItemId" + str(i)] = tvshow.itemId

                i += 1
                if i > 8:
                    break

            similar = Similar.from_dictionary(dic)
            Database().add_similar(similar)
            similar_tvshows = Database().get_similar_of_item_id(item_id)

        return similar_tvshows


    # album

    def search_album(self, title: str, duration: int) -> Album:
        track = Database().search_track(title)

        if track is not None:
            album = Database().get_album_by_item_id(track.parentId)
            return album

        #TODO: @Client choose an api and adapt this function accordingly
        api = None
        # TODO: @Client do api call to find album data using track name
        search_result = None

        if search_result is not None:
            album = search_result.album
            tracks = search_result.tracks
            artist = search_result.artist

            # TODO: @Client do api call to poster url
            poster_url = ""

            album = self.add_new_album_to_database(album, artist, tracks, poster_url)

            return album
        else:
            return None

    def search_albums(self, title: str, max_albums: int) -> Album:
        albums = Database().search_albums(title)

        if len(albums) >= max_albums:
            albums = albums[:max_albums]
            return albums

        #TODO: @Client choose an api and adapt this function accordingly
        api = None
        # TODO: @Client do api call to find album data using track name
        search_results = None

        for search_result in search_results:
            album = search_result.album
            tracks = search_result.tracks
            artist = search_result.artist

            # TODO: @Client do api call to poster url
            poster_url = ""

            album = self.add_new_album_to_database(album, artist, tracks, poster_url)

            albums.append(album)

        return albums

    def add_new_album_to_database(self, album, artist, tracks, poster_url) -> Album :
        album.itemId = Database().get_new_item_id()
        album.posterURL = poster_url

        if artist is not None:
            if Database().get_contributor_by_name(artist.name) is None:
                Database().add_contributor(artist)

            artist = Database().get_contributor_by_name(artist.name)

            album.artist = artist.id
        else:
            album.artist = None

        for t in tracks:
            t.itemId = Database().get_new_item_id()
            t.parentId = album.itemId
            Database().add_track(t)

        Database().add_album(album)

        # Init album in ratings
        db_rating = Rating()
        db_rating.clientId = "server"
        db_rating.userId = 0
        db_rating.itemId = album.itemId
        db_rating.rating = 0.0

        Database().add_rating(db_rating)

        return album

    #Expects parent album to exist
    def add_new_track_to_database(self, track) -> Track:
        if Database().get_album_by_item_id(track.parentId) is not None:
            track.itemId = Database().get_new_item_id()
            Database().add_track(track)
            return track
        else:
            return None

    def get_all_tracks(self, item_id: int) -> [Track]:
        return Database().get_tracks_of_item_id(item_id)

    def get_similar_albums(self, item_id: int) -> [Album]:
        requested_album = Database().get_album_by_item_id(item_id)
        similar_albums = Database().get_similar_of_item_id(item_id)

        if len(similar_albums) == 0:
            # TODO: @Client choose an api and adapt this function accordingly
            api = None
            # TODO: @Client use api to find similar albums
            api_albums = []
            dic = {"itemId": requested_album.itemId}
            i = 1

            for api_album in api_albums:
                # album already in database
                #TODO: @Client check in db if album is already present using api_album
                album = None

                if album is not None:
                    dic["otherItemId" + str(i)] = album.itemId
                else:
                    # TODO: @Client use api to find album
                    search_result = None

                    if search_result is None:
                        continue

                    album = search_result.album
                    tracks = search_result.tracks
                    artist = search_result.artist

                    # TODO: @Client do api call to poster url
                    poster_url = ""

                    album = self.add_new_album_to_database(album, artist, tracks, poster_url)
                    dic["otherItemId" + str(i)] = album.itemId

                i += 1
                if i > 8:
                    break

            similar = Similar.from_dictionary(dic)
            Database().add_similar(similar)
            similar_albums = Database().get_similar_of_item_id(item_id)

        return similar_albums