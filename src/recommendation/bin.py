import pandas as pd
import numpy as np

def vectors_distances(a, b):
    return np.linalg.norm(a - b)

class Models:
    BASE_FOLDER_PATH = './data/'
    
    def __init__(self):
        self.movies = self.prepare_movies()
        self.ratings = self.prepare_ratings()

    def prepare_movies(self):
        movies  = pd.read_csv(f'{self.BASE_FOLDER_PATH}movies.csv')
        movies =  movies.set_index('movieId')
        return movies

    def prepare_ratings(self):
        ratings  = pd.read_csv(f'{self.BASE_FOLDER_PATH}ratings.csv')
        return ratings
    
    def get_rating_by_user_id(self, user_id, columns=['movieId', 'rating']):
        data = self.ratings.query('userId==%d' % user_id)
        return data[columns].set_index('movieId')

    def two_users_joined(self, user_id_a, user_id_b, lsuffix='_a', rsuffix='_b'):
        user_a = self.get_rating_by_user_id(user_id_a)
        user_b = self.get_rating_by_user_id(user_id_b)
        return user_a.join(user_b, lsuffix=lsuffix, rsuffix=rsuffix).dropna()  

class Recommendation:

    def __init__(
        self, 
        user_in_evidence, 
        max_len_to_collect=None,
        min_calibration=5
    ):
        self.model = Models()
        self.user_in_evidence =  user_in_evidence
        self.max_len_to_collect = max_len_to_collect
        self.users = self.model.ratings['userId'].unique()
        self.min_calibration = min_calibration

    def check_calibration(self, value):
        return len(value) < self.min_calibration
           
    def user_distance(self, user_id_a, user_id_b):
        
        joined_list = self.model.two_users_joined(user_id_a, user_id_b)
        
        if self.check_calibration(joined_list):
            return (user_id_a, user_id_b,  None)

        rating_user_a = joined_list['rating_a']
        rating_user_b = joined_list['rating_b']
        distance = vectors_distances(rating_user_a,rating_user_b)
        return (user_id_a, user_id_b, distance)

    def distance_of_all(self):
        users = self.users
        if self.max_len_to_collect:
            users = self.users[:self.max_len_to_collect]
        distances = [ self.user_distance(self.user_in_evidence, user) for user in users]
        distances = list(filter(None, distances))
        return pd.DataFrame(distances, columns=['reference', 'user', 'distance'])

    def define_closest_user(self):
        all_distances = self.distance_of_all()
        all_distances = all_distances.set_index('user')
        all_distances = all_distances.sort_values('distance')
        all_distances = all_distances.drop(self.user_in_evidence)
        return all_distances.iloc[0].name

    def suggest_movies(self):
        closest_user = self.define_closest_user()
        user_in_evidence_rating = self.model.get_rating_by_user_id(self.user_in_evidence)
        closest_user_rating = self.model.get_rating_by_user_id(closest_user)
        
        to_suggest =  closest_user_rating.drop(
            user_in_evidence_rating.index,
            errors='ignore'
        )
        to_suggest = to_suggest.sort_values('rating', ascending=False)
        to_suggest = to_suggest.head()
        
        return  to_suggest.join(self.model.movies)

suggested_movies = Recommendation(1).suggest_movies()

print(suggested_movies)