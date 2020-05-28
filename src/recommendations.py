"""
Recommendation generator class
Supply with a bunch of Rating objects depicting what score users gave to items
And generate recommendations for those items

Also used to keep the database's recommendations up to date
"""

import pandas as pd

from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from database import Database, Album, TvShow, Movie
import database
from singleton import Singleton

RECOMMENDATION_AMOUNT = 20


# Class to store data needed by the recommendation algorithm
class Rating:
    def __init__(self, user_id: int, item_id: int, rating: float):
        self.user_id = user_id
        self.item_id = item_id
        self.rating = rating

    def __str__(self):
        return "User with id {} had given item with id {} a rating of {}".format(self.user_id, self.item_id,
                                                                                 self.rating)


# Class to store data outputted by the recommendation algorithm
class Recommendation:
    def __init__(self):
        self.item_id = None
        self.recommended_item_id = None
        self.distance = None

    def __str__(self) -> str:
        return "Item {} matches item {} about {}%".format(self.item_id, self.recommended_item_id,
                                                          int(self.distance * 100))


# Class to keep the database recommendations up to date
class RecommendationSyncer:
    def __init__(self):
        pass

    # Update all user ratings in the database
    def update_user_ratings(self, client_id: str, user_id: int, favorite_ids: [int], bookmarked_ids: [int], watched_ids: [int]):
        # Clear old stuff
        Database().clear_client_user_ratings(client_id, user_id)

        all_ids = list(set().union(favorite_ids, bookmarked_ids, watched_ids))
        all_ids.sort()

        # Calculate a score for each item and add to database
        for item_id in all_ids:
            rating = 0.0

            if item_id in favorite_ids:
                rating += 3

            if item_id in bookmarked_ids:
                rating += 1

            if item_id in watched_ids:
                rating += 2

            db_rating = database.Rating()
            db_rating.clientId = client_id
            db_rating.userId = user_id
            db_rating.itemId = item_id
            db_rating.rating = rating

            Database().add_rating(db_rating)


# Class to generate new recommendations based on data received by the database
class RecommendationGenerator(metaclass=Singleton):
    def __init__(self):
        self.model_knn = None
        self.data = None
        self.item_ids = []
        self.loaded = False

    # Checks if the generator has loaded yet
    def is_loaded(self) -> bool:
        return self.loaded

    # Generate recommendations for a specific user
    def generate_user_recommendations(self, client_id: str, user_id: int) -> {}:
        ratings = Database().get_ratings_of_client_user(client_id, user_id)

        movie_ids = []
        tvshow_ids = []
        album_ids = []

        for rating in ratings:
            # Add item ids while we don't have max
            if len(movie_ids) <= RECOMMENDATION_AMOUNT and Database().get_movie_by_item_id(rating.itemId) is not None:
                movie_ids.append(rating.itemId)
            elif len(movie_ids) <= RECOMMENDATION_AMOUNT and Database().get_movie_by_item_id(rating.itemId) is not None:
                tvshow_ids.append(rating.itemId)
            elif len(movie_ids) <= RECOMMENDATION_AMOUNT and Database().get_movie_by_item_id(rating.itemId) is not None:
                album_ids.append(rating.itemId)

            # If everything is maxed out and there are still ratings, stop
            if len(movie_ids) >= RECOMMENDATION_AMOUNT and len(tvshow_ids) >= RECOMMENDATION_AMOUNT and len(album_ids) >= RECOMMENDATION_AMOUNT:
                break

        recommendations = []

        for item_id in movie_ids:
            recommendations += self.generate(item_id, RECOMMENDATION_AMOUNT)

        for item_id in tvshow_ids:
            recommendations += self.generate(item_id, RECOMMENDATION_AMOUNT)

        for item_id in album_ids:
            recommendations += self.generate(item_id, RECOMMENDATION_AMOUNT)

        movie_recommendations: [Movie] = []
        tvshow_recommendations: [TvShow] = []
        album_recommendations: [Album] = []

        recommendations.sort(key=lambda x: x.distance, reverse=False)

        def check_rec_in_list(item_id: int, l: []):
            for i in l:
                if i.itemId == item_id:
                    return True

            return False

        for recommendation in recommendations:
            movie = Database().get_movie_by_item_id(recommendation.recommended_item_id)
            if movie is not None:
                if len(movie_recommendations) < RECOMMENDATION_AMOUNT and not check_rec_in_list(recommendation.recommended_item_id, movie_recommendations):
                    movie_recommendations.append(movie)
                continue

            tvshow = Database().get_tvshow_by_item_id(recommendation.recommended_item_id)
            if tvshow is not None:
                if len(tvshow_recommendations) < RECOMMENDATION_AMOUNT and not check_rec_in_list(recommendation.recommended_item_id, tvshow_recommendations):
                    tvshow_recommendations.append(tvshow)
                continue

            album = Database().get_album_by_item_id(recommendation.recommended_item_id)
            if album is not None:
                if len(album_recommendations) < RECOMMENDATION_AMOUNT and not check_rec_in_list(recommendation.recommended_item_id, album_recommendations):
                    album_recommendations.append(album)
                continue

        return {"movies": movie_recommendations, "tvshows": tvshow_recommendations, "albums": album_recommendations}

    # Reload the generator's internal data
    def reload_data(self, ratings: [Rating]) -> None:
        # Put rating data objects into proper array formats
        user_id_array = []
        item_id_array = []
        rating_array = []

        max_item_id = 0
        for rating in ratings:
            if rating.item_id > max_item_id:
                max_item_id = rating.item_id

        for rating in ratings:
            user_id_array.append(rating.user_id)
            item_id_array.append(rating.item_id)
            rating_array.append(rating.rating)

        # Store all item ids uniquely and sorted for later use
        self.item_ids.clear()
        self.item_ids = item_id_array.copy()
        self.item_ids = list(dict.fromkeys(self.item_ids))
        self.item_ids.sort()

        # Put data in a dataframe
        df_ratings = pd.DataFrame(data={"userId": user_id_array,
                                        "itemId": item_id_array,
                                        "rating": rating_array})

        # Pivot and create item-user matrix
        item_user_mat = df_ratings.pivot(index='itemId', columns='userId', values='rating').fillna(0)

        # Transform matrix to scipy sparse matrix
        self.data = csr_matrix(item_user_mat.values)

        # Define model
        self.model_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)

        # Fit
        self.model_knn.fit(self.data)

        self.loaded = True

    # Generate a certain amount of recommended items for an item
    def generate(self, item_id: int, max_recommendations: int = 1) -> [Recommendation]:
        # If the object has not yet loaded any data in, we can't give anything back
        if not self.loaded:
            return []

        # If we don't know anything about a certain item, we can't give anything back
        if item_id not in self.item_ids:
            return []

        # Don't try getting more recommendations than there are other items in the database
        if max_recommendations > len(self.item_ids)-1:
            max_recommendations = len(self.item_ids)-1

        # Fit
        self.model_knn.fit(self.data)

        # Get input item index
        idx = None
        for i in range(len(self.item_ids)):
            if self.item_ids[i] == item_id:
                idx = i

        distances, indices = self.model_knn.kneighbors(self.data[idx], n_neighbors=max_recommendations + 1)

        raw_recommends = sorted(list(zip(indices.squeeze().tolist(), distances.squeeze().tolist())),
                                key=lambda x: x[1])[:0:-1]

        recommendations = []

        # Create recommendation objects to return
        for i, (idx, dist) in enumerate(raw_recommends):
            rec = Recommendation()
            rec.item_id = item_id
            # Idx is the index of the item's id that is being recommended, not the actual item id
            # Therefore get it from item_ids
            rec.recommended_item_id = self.item_ids[idx]
            rec.distance = 1-dist

            recommendations.append(rec)

        # Recommendations gave the opposite of what you'd expect, so reverse them
        recommendations.reverse()

        return recommendations

    # Reload the ratings from the database into the generator
    def reload_ratings_from_database(self):
        db_ratings = Database().get_ratings()
        ratings = []
        unique_keys = {}

        for db_rating in db_ratings:
            db_client_id = db_rating.clientId
            db_user_id = db_rating.userId

            unique_key = db_client_id + str(db_user_id)
            integer_key = None

            if unique_key in unique_keys:
                integer_key = unique_keys[unique_key]
            else:
                integer_key = len(unique_keys) + 1
                unique_keys[unique_key] = integer_key

            ratings.append(Rating(integer_key, db_rating.itemId, db_rating.rating))

        self.reload_data(ratings)


if __name__ == '__main__':
    item_id = 1

    ratings = [Rating(1, 1, 5.0), Rating(1, 2, 5.0), Rating(2, 1, 5.0), Rating(3, 1, 5.0), Rating(3, 2, 5.0),
               Rating(4, 1, 5.0), Rating(4, 2, 5.0), Rating(4, 3, 5.0), Rating(4, 20, 1.0), Rating(4, 80, 1.0),
               Rating(5, 1, 5.0), Rating(5, 2, 5.0), Rating(5, 3, 5.0), Rating(5, 90, 5.0)]

    # ratings = [Rating(1, 1, 5.0), Rating(1, 2, 5.0), Rating(1, 80, 5.0), Rating(1, 20, 1.0), Rating(2, 20, 5.0)]

    RecommendationGenerator().reload_data(ratings)
    recs = RecommendationGenerator().generate(item_id, 300)

    print("Giving recommendations of item: ", item_id)
    for r in recs:
        print(r)
