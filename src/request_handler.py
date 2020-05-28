from meta_finder import MetaFinder
from database import Database
import request_handler_pb2 as rh
import request_handler_pb2_grpc as rh_grpc
from recommendations import RecommendationGenerator, Rating, RecommendationSyncer


# Parse a video item into a grpc response
def parse_videoitem(response, item):
    # Parse itemdata into response
    response.item.repo_id = int(item.itemId or 0)
    response.item.title = str(item.title or "")
    response.item.poster_url = str(item.posterURL or "")
    response.item.description = str(item.description or "")
    response.item.director = int(item.director or 0)
    response.item.runtime = int(item.runtime or 0)
    response.item.genre = str(item.genre or "")
    response.item.release_year = int(item.releaseYear or 0)
    response.item.avg_rating = float(item.avgRating or 0.0)


# Parse an album item into a grpc response
def parse_albumitem(response, item):
    # Parse itemdata into response
    response.item.repo_id = int(item.itemId or 0)
    response.item.title = str(item.title or "")
    response.item.poster_url = str(item.posterURL or "")
    response.item.artist = int(item.artist or 0)
    response.item.genre = str(item.genre or "")
    response.item.release_year = int(item.releaseYear or 0)
    response.item.avg_rating = float(item.avgRating or 0.0)


# Parse a contributor into a grpc response
def parse_contributor(response, item):
    # Parse contributors into response (find director using director id from item)
    contributors = MetaFinder().get_all_contributors(item.itemId, item.director)
    for c in contributors:
        contributor = rh.Contributor()
        contributor.id = int(c.id or 0)
        contributor.name = str(c.name or "")
        response.contributor.append(contributor)


"""
gRPC request handlers
"""


# Handler for movie requests
class MovieRequestHandler(rh_grpc.MovieDataServicer):
    def GetMovieData(self, request, context):
        response = rh.MovieResponse()

        if Database().check_client_id(request.client_id):
            # Get moviedata from metafinder
            movie = MetaFinder().search_movie(request.title, request.duration)
            if movie is not None:
                # Parse moviedata into response
                parse_videoitem(response, movie)

                # Parse contributors
                parse_contributor(response, movie)

        # Return response
        return response


# Handler for tv show requests
class TvShowRequestHandler(rh_grpc.TvShowDataServicer):
    def GetTvShowData(self, request, context):
        response = rh.TvShowResponse()

        if Database().check_client_id(request.client_id):
            # Get tvshowdata from metafinder
            tvshow = MetaFinder().search_tvshow(request.title, request.duration)

            if tvshow is not None:
                # Parse tvshowdata into response
                parse_videoitem(response, tvshow)

                # Parse contributors
                parse_contributor(response, tvshow)

                # Parse episodes into response
                episodes = MetaFinder().get_all_episodes(tvshow.itemId)
                for e in episodes:
                    episode = rh.Episode()
                    episode.repo_id = int(e.itemId or 0)
                    episode.episode = int(e.episode or 0)
                    episode.season = int(e.season or 0)
                    response.episode.append(episode)

        # Return response
        return response


# Handler for album requests
class AlbumRequestHandler(rh_grpc.AlbumDataServicer):
    def GetAlbumData(self, request, context):
        response = rh.AlbumResponse()

        if Database().check_client_id(request.client_id):
            # Get albumdata from metafinder
            album = MetaFinder().search_album(request.title, request.duration)

            if album is not None:
                # Parse albumdata into response
                parse_albumitem(response, album)

                # Parse contributor
                a = MetaFinder().get_director_or_artist(album.artist)
                artist = response.artist
                artist.id = int(a.id or 0)
                artist.name = str(a.name or "")

                # Parse tracks into response
                tracks = MetaFinder().get_all_tracks(album.itemId)
                for t in tracks:
                    track = rh.Track()
                    track.repo_id = int(t.itemId or 0)
                    track.title = str(t.title or "")
                    response.track.append(track)

        # Return response
        return response


# Handler for the movie fix request
class FixMoviesRequestHandler(rh_grpc.FixMovieDataServicer):
    def GetMoviesData(self, request, context):
        response = rh.MoviesResponse()

        if Database().check_client_id(request.client_id):
            # Get 10 movies from metafinder
            movies = MetaFinder().search_movies(request.title, 10)

            for movie in movies:
                if movie is None:
                    continue

                movie_response = rh.MovieResponse()

                # Parse moviedata into response
                parse_videoitem(movie_response, movie)

                # Parse contributors
                parse_contributor(movie_response, movie)

                response.movie.append(movie_response)

        # Return response
        return response


# Handler for the tv show fix request
class FixTvShowsRequestHandler(rh_grpc.FixTvShowDataServicer):
    def GetTvShowsData(self, request, context):
        response = rh.TvShowsResponse()

        if Database().check_client_id(request.client_id):
            # Get 10 tvshows from metafinder
            tvshows = MetaFinder().search_tvshows(request.title, 10)

            for tvshow in tvshows:
                if tvshow is None:
                    continue

                tvshow_response = rh.TvShowResponse()

                # Parse tvshowdata into response
                parse_videoitem(tvshow_response, tvshow)

                # Parse contributors
                parse_contributor(tvshow_response, tvshow)

                # Parse episodes into response
                episodes = MetaFinder().get_all_episodes(tvshow.itemId)
                for e in episodes:
                    episode = rh.Episode()
                    episode.repo_id = int(e.itemId or 0)
                    episode.episode = int(e.episode or 0)
                    episode.season = int(e.season or 0)
                    tvshow_response.episode.append(episode)

                response.tvshow.append(tvshow_response)

        # Return response
        return response


# Handler for the album fix request
class FixAlbumsRequestHandler(rh_grpc.FixAlbumDataServicer):
    def GetAlbumsData(self, request, context):
        response = rh.AlbumsResponse()

        if Database().check_client_id(request.client_id):
            # Get 10 albums from metafinder
            albums = MetaFinder().search_albums(request.title, 10)

            for album in albums:
                if album is None:
                    continue

                album_response = rh.AlbumResponse()

                # Parse albumdata into response
                parse_albumitem(album_response, album)

                # Parse contributor
                a = MetaFinder().get_director_or_artist(album.artist)
                artist = album_response.artist
                artist.id = int(a.id or 0)
                artist.name = str(a.name or "")

                # Parse tracks into response
                tracks = MetaFinder().get_all_tracks(album.itemId)
                for t in tracks:
                    track = rh.Track()
                    track.repo_id = int(t.itemId or 0)
                    track.title = str(t.title or "")
                    album_response.track.append(track)

                response.album.append(album_response)

        # Return response
        return response


# Handler for the similar movies request
class SimilarMoviesRequestHandler(rh_grpc.SimilarMovieDataServicer):
    def GetSimilarMovieData(self, request, context):
        response = rh.MoviesResponse()

        if Database().check_client_id(request.client_id):
            # Get moviedata from metafinder
            movies = MetaFinder().get_similar_movies(request.repo_id)

            for movie in movies:
                if movie is None:
                    continue

                movie_response = rh.MovieResponse()

                # Parse moviedata into response
                parse_videoitem(movie_response, movie)

                # Parse contributors
                parse_contributor(movie_response, movie)

                response.movie.append(movie_response)

        # Return response
        return response


# Handler for the similar tv shows request
class SimilarTvShowsRequestHandler(rh_grpc.SimilarTvShowDataServicer):
    def GetSimilarTvShowData(self, request, context):
        response = rh.TvShowsResponse()

        if Database().check_client_id(request.client_id):
            # Get tvshowdata from metafinder
            tvshows = MetaFinder().get_similar_tvshows(request.repo_id)

            for tvshow in tvshows:
                if tvshow is None:
                    continue

                tvshow_response = rh.TvShowResponse()

                # Parse tvshowdata into response
                parse_videoitem(tvshow_response, tvshow)

                # Parse contributors
                parse_contributor(tvshow_response, tvshow)

                # Parse episodes into response
                episodes = MetaFinder().get_all_episodes(tvshow.itemId)
                for e in episodes:
                    episode = rh.Episode()
                    episode.repo_id = int(e.itemId or 0)
                    episode.episode = int(e.episode or 0)
                    episode.season = int(e.season or 0)
                    tvshow_response.episode.append(episode)

                response.tvshow.append(tvshow_response)

        # Return response
        return response


# Handler for the similar albums request
class SimilarAlbumsRequestHandler(rh_grpc.SimilarAlbumDataServicer):
    def GetSimilarAlbumData(self, request, context):
        response = rh.AlbumsResponse()

        if Database().check_client_id(request.client_id):
            # Get albumdata from metafinder
            albums = MetaFinder().get_similar_albums(request.repo_id)

            for album in albums:
                if album is None:
                    continue

                album_response = rh.AlbumResponse()

                # Parse albumdata into response
                parse_albumitem(album_response, album)

                # Parse contributor
                a = MetaFinder().get_director_or_artist(album.artist)
                artist = album_response.artist
                artist.id = int(a.id or 0)
                artist.name = str(a.name or "")

                # Parse tracks into response
                tracks = MetaFinder().get_all_tracks(album.itemId)
                for t in tracks:
                    track = rh.Track()
                    track.repo_id = int(t.itemId or 0)
                    track.title = str(t.title or "")
                    album_response.track.append(track)

                response.album.append(album_response)

        # Return response
        return response


# Handler for the recommendation request
class RecommendationsRequestHandler(rh_grpc.RecommendationsDataServicer):
    def GetRecommendationsData(self, request, context):
        response = rh.RecommendationsResponse()

        if Database().check_client_id(request.client_id):
            RecommendationSyncer().update_user_ratings(request.client_id, request.user_id, request.favorite_ids, request.bookmarked_ids, request.watched_ids)

            RecommendationGenerator().reload_ratings_from_database()
            recommendations = RecommendationGenerator().generate_user_recommendations(request.client_id, request.user_id)

            for movie in recommendations["movies"]:
                movie_response = rh.MovieResponse()

                # Parse moviedata into response
                parse_videoitem(movie_response, movie)

                # Parse contributors
                parse_contributor(movie_response, movie)

                response.movie.append(movie_response)

            for tvshow in recommendations["tvshows"]:
                tvshow_response = rh.TvShowResponse()

                # Parse tvshowdata into response
                parse_videoitem(tvshow_response, tvshow)

                # Parse contributors
                parse_contributor(tvshow_response, tvshow)

                # Parse episodes into response
                episodes = MetaFinder().get_all_episodes(tvshow.itemId)
                for e in episodes:
                    episode = rh.Episode()
                    episode.repo_id = int(e.itemId or 0)
                    episode.episode = int(e.episode or 0)
                    episode.season = int(e.season or 0)
                    tvshow_response.episode.append(episode)

                response.tvshow.append(tvshow_response)

            for album in recommendations["albums"]:
                album_response = rh.AlbumResponse()

                # Parse albumdata into response
                parse_albumitem(album_response, album)

                # Parse contributor
                a = MetaFinder().get_director_or_artist(album.artist)
                artist = album_response.artist
                artist.id = int(a.id or 0)
                artist.name = str(a.name or "")

                # Parse tracks into response
                tracks = MetaFinder().get_all_tracks(album.itemId)
                for t in tracks:
                    track = rh.Track()
                    track.repo_id = int(t.itemId or 0)
                    track.title = str(t.title or "")
                    album_response.track.append(track)

                response.album.append(album_response)

        # Return response
        return response


# Handler for the client linking request
class LinkClientHandler(rh_grpc.LinkClientServicer):
    def AddClient(self, request, context):
        response = rh.IdResponse()

        data = Database().get_licensekey_data(request.data)
        if data is not None:
            if data["usedClients"] < data["maxClients"]:
                Database().update_used_clients(data["licenseId"], data["usedClients"] + 1)
                response.client_id = Database().add_new_client_id(data["licenseId"])
                response.message = "Activation Successful"
            else:
                response.message = "License key full"
        else:
            response.message = "Invalid license key"
        # Return response
        return response


# Handler for the client unlinking request
class UnlinkClientHandler(rh_grpc.UnlinkClientServicer):
    def RemoveClient(self, request, context):
        response = rh.IdResponse()

        client_data = Database().get_client_data(request.data)

        if client_data is not None:
            Database().remove_client_id(request.data)
            license_key_data = Database().get_licensekey_data_by_id(client_data["licenseId"])
            Database().update_used_clients(license_key_data["licenseId"], license_key_data["usedClients"] - 1)
            response.client_id = ""
            response.message = "Deactivation Successful"
        else:
            response.message = "Already Deactivated"
        # Return response
        return response
