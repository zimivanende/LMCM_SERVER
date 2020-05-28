import grpc
from concurrent import futures
import time
from database import Database

# import the generated classes
import request_handler_pb2 as rh
import request_handler_pb2_grpc as rh_grpc

# import the original calculator.py
from request_handler import MovieRequestHandler, TvShowRequestHandler, AlbumRequestHandler, FixMoviesRequestHandler, FixTvShowsRequestHandler, FixAlbumsRequestHandler, SimilarMoviesRequestHandler, SimilarTvShowsRequestHandler, SimilarAlbumsRequestHandler, RecommendationsRequestHandler, LinkClientHandler, UnlinkClientHandler

# create a gRPC server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

# use the generated function `add_CalculatorServicer_to_server`
# to add the defined class to the server
rh_grpc.add_MovieDataServicer_to_server(
        MovieRequestHandler(), server)
rh_grpc.add_TvShowDataServicer_to_server(
        TvShowRequestHandler(), server)
rh_grpc.add_AlbumDataServicer_to_server(
        AlbumRequestHandler(), server)
rh_grpc.add_FixMovieDataServicer_to_server(
        FixMoviesRequestHandler(), server)
rh_grpc.add_FixTvShowDataServicer_to_server(
        FixTvShowsRequestHandler(), server)
rh_grpc.add_FixAlbumDataServicer_to_server(
        FixAlbumsRequestHandler(), server)
rh_grpc.add_SimilarMovieDataServicer_to_server(
        SimilarMoviesRequestHandler(), server)
rh_grpc.add_SimilarTvShowDataServicer_to_server(
        SimilarTvShowsRequestHandler(), server)
rh_grpc.add_SimilarAlbumDataServicer_to_server(
        SimilarAlbumsRequestHandler(), server)
rh_grpc.add_RecommendationsDataServicer_to_server(
        RecommendationsRequestHandler(), server)
rh_grpc.add_LinkClientServicer_to_server(
        LinkClientHandler(), server)
rh_grpc.add_UnlinkClientServicer_to_server(
        UnlinkClientHandler(), server)

# Developer license key
dev_key = Database().get_licensekey_data_by_id(1)

if dev_key is None:
    print("Developer key (available clients = 1000): " + Database().add_new_license_key(1000))
elif dev_key["usedClients"] == dev_key["maxClients"]:
    Database().update_max_clients_licensekey_by_id(1, dev_key["maxClients"] + 1000)
    dev_key = Database().get_licensekey_data_by_id(1)
    print("Developer key (available clients = " + str(dev_key["maxClients"] - dev_key["usedClients"]) + "): " + dev_key["licenseKey"])
else:
    print("Developer key (available clients = " + str(dev_key["maxClients"] - dev_key["usedClients"]) + "): " + dev_key["licenseKey"])

# listen on port 50051
print('Starting server. Listening on port 50051.')
server.add_insecure_port('[::]:50051')
server.start()

# since server.start() will not block,
# a sleep-loop is added to keep alive
try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)
