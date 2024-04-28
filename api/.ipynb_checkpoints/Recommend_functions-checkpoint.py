import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random
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
        print(self.ratings.head())
        self.movies = self.movies[self.movies['genres'] != '(no genres listed)']

        self.user_movie_matrix = self.ratings.pivot_table(index='userId', columns='movieId_id', values='rating').fillna(0)
        self.user_movie_matrix = self.user_movie_matrix.rename(columns={'movieId_id': 'movieId'})
        self.user_similarities = cosine_similarity(self.user_movie_matrix)

        self.movie_tags = pd.merge(self.tags, self.movies, left_on='movieId_id', right_on='movieId')
        self.movie_tags = self.movie_tags.drop(columns=['movieId_id'])

        self.mood_genre_mapping = {
            "Joy": ['Adventure', 'Children', 'Fantasy', 'Comedy', 'Romance', 'Documentary', 'Musical', 'Animation'],
            "Sadness": ['Drama', 'Thriller', 'Mystery', 'War', 'Action', 'Crime', 'Western', 'Film-Noir'],
            "Anger": ['Action', 'Crime', 'Western', 'Film-Noir'],
            "Fear": ['Horror', 'Sci-Fi'],
            "Disgust": ['Action', 'Crime', 'Western', 'Film-Noir']
        }

        self.previously_recommended_ids=[]


    def mood_filtered_tag_recommendations(self, user_id, mood):
        # Ensure TF-IDF matrix for tags is created
        if not hasattr(self, 'tfidf_matrix'):
            self.movie_tags['all_tags'] = self.movie_tags.groupby('movieId')['tag'].transform(lambda x: ' '.join(x.unique()))
            self.tfidf_vectorizer = TfidfVectorizer()
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.movie_tags['all_tags'].unique())

        # Filter movies by mood-related genres
        mood_genres = self.mood_genre_mapping[mood]
        mood_filtered_movies = self.movies[self.movies['genres'].apply(lambda x: any(genre in x for genre in mood_genres))]

        # Get the IDs of movies the user has already watched
        watched_movie_ids_series = self.ratings[self.ratings['userId'] == int(user_id)]['movieId_id']
        watched_movie_ids = set(watched_movie_ids_series.unique())

        # Check if there are no watched movies for the user
        if watched_movie_ids_series.empty:
            return "No watched movies found for the user."

        # Combine watched movies with previously recommended movies
        all_excluded_movie_ids = watched_movie_ids.union(self.previously_recommended_ids)

        # Exclude recommended movies when creating candidate_movies
        candidate_movies = mood_filtered_movies[~mood_filtered_movies['movieId'].isin(all_excluded_movie_ids)]
        print(candidate_movies.head())

        if candidate_movies.empty:
            return "No suitable recommendations based on your mood and preferences at the moment."

        # Calculate similarity between candidate movies and all movies using TF-IDF matrix
        candidate_indices = []
        for movie_id in candidate_movies['movieId']:
            indices = self.movie_tags[self.movie_tags['movieId'] == int(movie_id)].index
            if not indices.empty:
                candidate_indices.append(indices[0])
            else:
                print(f"No index found for movie ID: {movie_id}")

        # Filter out movie IDs without corresponding indices
        candidate_indices = [idx for idx in candidate_indices if idx < self.tfidf_matrix.shape[0]]  # Using shape[0]

        print("Filtered candidate indices:", candidate_indices)

        valid_tfidf_matrix = self.tfidf_matrix[candidate_indices]
        print("hell3")
        all_tfidf_matrix = self.tfidf_matrix
        tag_similarities = cosine_similarity(valid_tfidf_matrix, all_tfidf_matrix)

        # Get recommended movie index with the highest average similarity
        mean_similarities = tag_similarities.mean(axis=1)
        max_sim_index = np.argmax(mean_similarities)

        # Ensure the index is referring to the filtered list of movies, not the original list
        recommended_movie_id = candidate_movies.iloc[max_sim_index]['movieId']
        recommended_movie_title = candidate_movies[candidate_movies['movieId'] == recommended_movie_id]['title'].iloc[0]
        print(f"Recommended movie: {recommended_movie_title}")

        # Add the recommended movie ID to previously recommended set
        self.previously_recommended_ids.append(recommended_movie_id)

        return recommended_movie_title

    def softmax(self, x, temperature):
        """Compute softmax values for each score in the vector x."""
        exp_x = np.exp(x / temperature)
        return exp_x / np.sum(exp_x)

    def apply_softmax_temperature(self, scores, temperature):
        """Adjust scores with softmax temperature."""
        scores_array = np.array(scores)  # Convert scores to a NumPy array
        adjusted_scores = scores_array / temperature  # Now this operation is element-wise
        return self.softmax(adjusted_scores, temperature)

    def content_based_recommendations(self, mood):
        genres = self.mood_genre_mapping[mood]
        recommended_movies = []
        for genre in genres:
            genre_movies = self.movies[self.movies['genres'].str.contains(genre)]
            recommended_movies.extend(genre_movies['title'].tolist())

        # Assign scores to recommended movies (e.g., randomly for illustration purposes)
        scores = [random.uniform(0, 1) for _ in recommended_movies]

        # Apply softmax temperature to adjust the scores
        adjusted_scores = self.apply_softmax_temperature(scores, 2.0)

        # Choose a movie based on adjusted scores
        recommended_index = np.random.choice(len(adjusted_scores), p=adjusted_scores)
        recommended_movie = recommended_movies[recommended_index]

        return recommended_movie
    
    def collaborative_filtering_recommendations(self, user_id, mood):
        genres = self.mood_genre_mapping[mood]
        # Filter movies by mood-related genres
        mood_filtered_movies = self.movies[self.movies['genres'].apply(lambda x: any(genre in x for genre in genres))]
        mood_filtered_movie_ids = mood_filtered_movies['movieId'].unique()
        
        # Ensure only movie IDs present in user_movie_matrix are considered
        valid_movie_ids = [movie_id for movie_id in mood_filtered_movie_ids if movie_id in self.user_movie_matrix.columns]

        # Filter the user_movie_matrix to only include mood-related movies that are valid
        mood_filtered_matrix = self.user_movie_matrix[valid_movie_ids]
        mood_filtered_matrix.fillna(0, inplace=True)
        
        # Compute similarities with the mood-filtered matrix
        user_similarities = cosine_similarity(mood_filtered_matrix)
        user_index = list(self.user_movie_matrix.index).index(int(user_id))
        user_sim_scores = list(enumerate(user_similarities[user_index]))
        user_sim_scores = sorted(user_sim_scores, key=lambda x: x[1], reverse=True)
        similar_users_indices = [i[0] for i in user_sim_scores[1:6]]  # Exclude the user itself
        similar_users_ratings = mood_filtered_matrix.iloc[similar_users_indices]
        user_ratings = mood_filtered_matrix.iloc[user_index]
        
        # Get movies highly rated by similar users but not rated by the current user
        recommended = similar_users_ratings.mean(axis=0) - user_ratings
        recommended = recommended[recommended > 0].sort_values(ascending=False)
        
        # Get the top recommended movie ID
        top_recommended_movie_id = recommended.index[0] if not recommended.empty else None
        if top_recommended_movie_id:
            top_recommended_movie = self.movies[self.movies['movieId'] == top_recommended_movie_id]['title'].iloc[0]
            return top_recommended_movie
        else:
            return None
        
    def update_user_preference(self, movie_id, action, user_id):
        # First, find the movie instance based on the title
        try:
            movie = Movie.objects.get(movieId=movie_id)
        except Movie.DoesNotExist:
            return "Movie not found."
        
        user_id = int(user_id)
        movie_id = int(movie_id)
      
        # Define the rating based on the action
        if action == "Like":
            self.user_movie_matrix.loc[user_id, movie_id] = 4
            return "Thanks for liking this movie!"
        elif action == "Dislike":
            self.user_movie_matrix.loc[user_id, movie_id] = 2
            return "Thanks for disliking this movie!"
        
    def process_user_action(self, movie_title, action, user_id, mood, type):
        """
        Process the user's action on a recommended movie and provide the next steps.

        Args:
            movie_title (str): The title of the recommended movie.
            action (str): The user's action ('Like', 'Dislike', 'Perfect').

        Returns:
            dict: A dictionary containing the next recommended movie (if any) and messages.
        """
        response = {
            'message': '',
            'next_recommendation': None,
            'action': action,
        }

        movie = Movie.objects.get(title=movie_title)
        movie_id = movie.movieId
        # Update user's rating based on the action
        update_message = self.update_user_preference(movie_id, action, user_id)
        response['message'] = update_message

        if action == "Perfect":
            response['message'] = " Thank you for using the recommendation system. Enjoy your movie!"
        elif action in ["Like", "Dislike"]:
            # Generate the next recommendation based on the user's mood
            # Assuming the mood is stored or passed as an attribute
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
    
    def refresh_data(self):
        # Re-fetch data from the database
        ratings_dj = Rating.objects.all()
        values_r = list(ratings_dj.values())
        ratings = pd.DataFrame(values_r)

        # Recalculate user_movie_matrix
        self.user_movie_matrix = ratings.pivot_table(index='userId', columns='movieId_id', values='rating').fillna(0)
        self.user_movie_matrix = self.user_movie_matrix.rename(columns={'movieId_id': 'movieId'})

        # Recalculate user_similarities
        self.user_similarities = cosine_similarity(self.user_movie_matrix)
