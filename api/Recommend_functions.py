import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.db.models import Q
from django.utils import timezone
import numpy as np

from api.models import Movie, Rating, Tag

class RecommendFunctions:
    
    def __init__(self):
        ratings_dj = Rating.objects.all()
        values_r = list(ratings_dj.values())
        self.ratings = pd.DataFrame(values_r)

        movies_dj = Movie.objects.all()
        values_m = list(movies_dj.values())
        self.movies = pd.DataFrame(values_m)

        tags_dj = Tag.objects.all()
        values_t = list(tags_dj.values())
        self.tags = pd.DataFrame(values_t)

        self.ratings_counts = self.ratings.groupby('userId').size()
        self.active_users = self.ratings_counts[self.ratings_counts >= 20].index
        self.ratings = self.ratings[self.ratings['userId'].isin(self.active_users)]
        self.movies = self.movies[self.movies['genres'] != '(no genres listed)']

        self.user_movie_matrix = self.ratings.pivot_table(index='userId', columns='movieId_id', values='rating').fillna(0)
        self.user_movie_matrix = self.user_movie_matrix.rename(columns={'movieId_id': 'movieId'})
        self.user_similarities = cosine_similarity(self.user_movie_matrix)

        self.movie_tags = pd.merge(self.tags, self.movies, left_on='movieId_id', right_on='movieId')
        self.movie_tags = self.movie_tags.drop(columns=['movieId_id'])
        print(self.movie_tags.head())

        self.mood_genre_mapping = {
            "Joy": ['Adventure', 'Children', 'Fantasy', 'Comedy', 'Romance', 'Documentary', 'Musical', 'Animation'],
            "Sadness": ['Drama', 'Thriller', 'Mystery', 'War', 'Action', 'Crime', 'Western', 'Film-Noir'],
            "Anger": ['Action', 'Crime', 'Western', 'Film-Noir'],
            "Fear": ['Horror', 'Sci-Fi'],
            "Disgust": ['Action', 'Crime', 'Western', 'Film-Noir']
        }

        self.previously_recommended_ids=[]


    # Function used to recommend movies to users based on content filtering, tags and mood. 
    # FUNCTION USED IN CONTENT- BASED SYSTEM
    def mood_filtered_tag_recommendations(self, user_id, mood):
        if not hasattr(self, 'tfidf_matrix'):
            self.movie_tags['all_tags'] = self.movie_tags.groupby('movieId')['tag'].transform(lambda x: ' '.join(x.unique()))
            self.tfidf_vectorizer = TfidfVectorizer()
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.movie_tags['all_tags'].unique())

        mood_genres = self.mood_genre_mapping[mood]
        mood_filtered_movies = self.movies[self.movies['genres'].apply(lambda x: any(genre in x for genre in mood_genres))]

        watched_movie_ids_series = self.ratings[self.ratings['userId'] == int(user_id)]['movieId_id']
        watched_movie_ids = set(watched_movie_ids_series.unique())

        if watched_movie_ids_series.empty:
            return "No watched movies found for the user."

        all_excluded_movie_ids = watched_movie_ids.union(self.previously_recommended_ids)

        candidate_movies = mood_filtered_movies[~mood_filtered_movies['movieId'].isin(all_excluded_movie_ids)]
        print(candidate_movies.head())

        if candidate_movies.empty:
            return "No suitable recommendations based on your mood and preferences at the moment."

        candidate_indices = []
        for movie_id in candidate_movies['movieId']:
            indices = self.movie_tags[self.movie_tags['movieId'] == int(movie_id)].index
            if not indices.empty:
                candidate_indices.append(indices[0])
            else:
                print(f"No index found for movie ID: {movie_id}")

        candidate_indices = [idx for idx in candidate_indices if idx < self.tfidf_matrix.shape[0]]  

        print("Filtered candidate indices:", candidate_indices)

        valid_tfidf_matrix = self.tfidf_matrix[candidate_indices]
        all_tfidf_matrix = self.tfidf_matrix
        tag_similarities = cosine_similarity(valid_tfidf_matrix, all_tfidf_matrix)

        mean_similarities = tag_similarities.mean(axis=1)
        max_sim_index = np.argmax(mean_similarities)

        recommended_movie_id = candidate_movies.iloc[max_sim_index]['movieId']
        recommended_movie_title = candidate_movies[candidate_movies['movieId'] == recommended_movie_id]['title'].iloc[0]
        print(f"Recommended movie: {recommended_movie_title}")

        self.previously_recommended_ids.append(recommended_movie_id)

        return recommended_movie_title

    # Calculate softmax values for each score in the vector x using temperature.
    def softmax(self, x, temperature):
        exp_x = np.exp(x / temperature)
        return exp_x / np.sum(exp_x)

    # Build user profile based on movies they have rated highly.
    def build_user_profile(self, user_id):
        user_id = int(user_id)
        high_rated = self.ratings[(self.ratings['userId'] == user_id) & (self.ratings['rating'] >= 3.8)]
        high_rated = high_rated.rename(columns={'movieId_id': 'movieId'})
        high_rated_movies = high_rated.merge(self.movie_tags, on='movieId')
        if high_rated_movies.empty:
            return None

        user_profile_tags = ' '.join(high_rated_movies['tag'].tolist())
        return self.tfidf_vectorizer.transform([user_profile_tags])
    
    # Recomend popular movies to users, if build_user_profile is not possible
    def recommend_popular_or_trending(self, mood):
        print(self.ratings.head())
        aggregated_ratings = self.ratings.groupby('movieId_id').agg(
            average_rating=('rating', 'mean'),
            rating_count=('rating', 'count')
        ).reset_index()

        aggregated_ratings = aggregated_ratings.rename(columns={'movieId_id': 'movieId'})

        movies_with_ratings = pd.merge(self.movies, aggregated_ratings, on='movieId', how='left')

        mood_genres = self.mood_genre_mapping[mood]
        mood_filtered_movies = movies_with_ratings[movies_with_ratings['genres'].apply(lambda x: any(genre in x for genre in mood_genres))]

        if mood_filtered_movies.empty:
            return "No movies available for this mood."

        mood_filtered_movies = mood_filtered_movies.sort_values(by=['average_rating', 'rating_count'], ascending=[False, False])

        return mood_filtered_movies.iloc[0]['title']
    
    # Content-based recommendation for the initial recommendation for both the systems
    def content_based_recommendations(self, mood, user_id, temperature=1.2):
        if not hasattr(self, 'tfidf_vectorizer'):
            self.movie_tags['all_tags'] = self.movie_tags.groupby('movieId')['tag'].transform(lambda x: ' '.join(x.unique()))
            self.tfidf_vectorizer = TfidfVectorizer()
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.movie_tags['all_tags'])

        user_profile = self.build_user_profile(user_id)
        print(user_profile)
        if user_profile is None:
            return self.recommend_popular_or_trending(mood)

        mood_genres = self.mood_genre_mapping[mood]
        mood_filtered_movies = self.movies[self.movies['genres'].apply(lambda x: any(genre in x for genre in mood_genres))]
        mood_filtered_movie_ids = mood_filtered_movies['movieId'].tolist()

        filtered_indices = [i for i, row in self.movie_tags.iterrows() if row['movieId'] in mood_filtered_movie_ids]
        filtered_tfidf_matrix = self.tfidf_matrix[filtered_indices]

        similarities = cosine_similarity(user_profile, filtered_tfidf_matrix).flatten()
        
        probabilities = self.softmax(similarities, temperature)

        chosen_index = np.random.choice(range(len(probabilities)), p=probabilities)
        chosen_movie_id = mood_filtered_movies.iloc[chosen_index]['movieId']
        recommended_movie_title = mood_filtered_movies[mood_filtered_movies['movieId'] == chosen_movie_id]['title'].iloc[0]

        return recommended_movie_title
    
    # Function used to recommend movies to users based on collanrative filtering, users and mood. 
    # FUNCTION USED IN COLLABORATIVE- BASED SYSTEM
    def collaborative_filtering_recommendations(self, user_id, mood):
        genres = self.mood_genre_mapping[mood]
        mood_filtered_movies = self.movies[self.movies['genres'].apply(lambda x: any(genre in x for genre in genres))]
        mood_filtered_movie_ids = mood_filtered_movies['movieId'].unique()
        
        valid_movie_ids = [movie_id for movie_id in mood_filtered_movie_ids if movie_id in self.user_movie_matrix.columns]

        mood_filtered_matrix = self.user_movie_matrix[valid_movie_ids]
        mood_filtered_matrix.fillna(0, inplace=True)
        
        user_similarities = cosine_similarity(mood_filtered_matrix)
        user_index = list(self.user_movie_matrix.index).index(int(user_id))
        user_sim_scores = list(enumerate(user_similarities[user_index]))
        user_sim_scores = sorted(user_sim_scores, key=lambda x: x[1], reverse=True)
        similar_users_indices = [i[0] for i in user_sim_scores[1:6]] 
        similar_users_ratings = mood_filtered_matrix.iloc[similar_users_indices]
        user_ratings = mood_filtered_matrix.iloc[user_index]
        
        recommended = similar_users_ratings.mean(axis=0) - user_ratings
        recommended = recommended[recommended > 0].sort_values(ascending=False)
        
        top_recommended_movie_id = recommended.index[0] if not recommended.empty else None
        if top_recommended_movie_id:
            top_recommended_movie = self.movies[self.movies['movieId'] == top_recommended_movie_id]['title'].iloc[0]
            return top_recommended_movie
        else:
            return None

    # Updates the movie rating based on user's interaction
    def update_user_preference(self, movie_id, action, user_id):
        user_id = int(user_id)
        movie_id = int(movie_id)
        
        try:
            movie = Movie.objects.get(movieId=movie_id)
        except Movie.DoesNotExist:
            return "Movie not found."

        new_rating_value = 3.5 if action == "Like" else 2 if action == "Dislike" else 4.5

        rating, created = Rating.objects.get_or_create(
            userId=user_id, 
            movieId=movie,
            defaults={
                'rating': new_rating_value,
                'timestamp': timezone.now() 
            }
        )
        
        if not created and new_rating_value is not None:
            rating.rating = new_rating_value
            rating.timestamp = timezone.now() 
            rating.save()
            response_message = "Rating updated successfully."
        elif created:
            response_message = "Thanks for rating this movie for the first time!"
        else:
            return "Invalid action."

        if action in ["Like", "Dislike"]:
            self.user_movie_matrix.loc[user_id, movie_id] = new_rating_value
        
        return response_message

        
    # Process the user's action on a recommended movie
    def process_user_action(self, movie_title, action, user_id, mood, type):
        response = {
            'message': '',
            'next_recommendation': None,
            'action': action,
        }

        movie = Movie.objects.get(title=movie_title)
        movie_id = movie.movieId
        update_message = self.update_user_preference(movie_id, action, user_id)
        response['message'] = update_message

        if action == "Perfect":
            response['message'] = " Thank you for using the recommendation system. Enjoy your movie!"
        elif action in ["Like", "Dislike"]:
            try:
                if type == "score":
                    print("Generating next recommendation based on the user's mood score.")
                    next_recommendation = self.collaborative_filtering_recommendations(user_id, mood)
                elif type == "tag":
                    print("Generating next recommendation based on the user's mood tags.")
                    next_recommendation = self.mood_filtered_tag_recommendations(user_id, mood)
                if next_recommendation:
                    response['next_recommendation'] = next_recommendation
                    response['message'] += " Based on your feedback, here's another recommendation."
                else:
                    response['message'] += " We're out of recommendations for now."
            except Exception as e:
                print(e)
                response['message'] += f" Error generating next recommendation: {e}"
        else:
            response['message'] += "Invalid choice. Please select from Like/Dislike/Perfect."

        return response
    
    # Re-fetch data from the database, Recalculate user_movie_matrix, Recalculate user_similarities
    def refresh_data(self):
        ratings_dj = Rating.objects.all()
        values_r = list(ratings_dj.values())
        ratings = pd.DataFrame(values_r)

        self.user_movie_matrix = ratings.pivot_table(index='userId', columns='movieId_id', values='rating').fillna(0)
        self.user_movie_matrix = self.user_movie_matrix.rename(columns={'movieId_id': 'movieId'})

        self.user_similarities = cosine_similarity(self.user_movie_matrix)
