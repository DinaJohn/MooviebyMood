from django.core.management.base import BaseCommand
from api.models import Movie, Rating, Tag, Link
import pandas as pd
import os
from django.utils import timezone

class Command(BaseCommand):
    help = 'Import data from CSV files'

    def handle(self, *args, **kwargs):
        self.stdout.write('Importing data...')

        csv_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../movielens_dataset'))
        movies_df = pd.read_csv(os.path.join(csv_dir, 'movies.csv'))
        ratings_df = pd.read_csv(os.path.join(csv_dir, 'ratings.csv'))
        tags_df = pd.read_csv(os.path.join(csv_dir, 'tags.csv'))

        # Import movies
        for _, row in movies_df.iterrows():
            movie = Movie.objects.create(
                movieId=row['movieId'],
                title=row['title'],
                genres=row['genres']
            )

        # Import ratings
        ratings_df['timestamp'] = pd.to_datetime(ratings_df['timestamp'], unit='s').apply(lambda x: timezone.make_aware(x, timezone.utc))
        for _, row in ratings_df.iterrows():
            movie_id = row['movieId']
            try:
                movie = Movie.objects.get(movieId=movie_id)
            except Movie.DoesNotExist:
                print(f"Movie with movieId {movie_id} does not exist. Skipping...")
                continue 
            rating = Rating.objects.create(
                userId=row['userId'],
                movieId = movie,
                rating=row['rating'],
                timestamp=row['timestamp']
            )


        # Import tags
        tags_df['timestamp'] = pd.to_datetime(tags_df['timestamp'], unit='s').apply(lambda x: timezone.make_aware(x, timezone.utc))
        for _, row in tags_df.iterrows():
            movie_id = row['movieId']
            try:
                movie = Movie.objects.get(movieId=movie_id)
            except Movie.DoesNotExist:
                print(f"Movie with movieId {movie_id} does not exist. Skipping...")
                continue
            tag = Tag.objects.create(
                userId=row['userId'],
                movieId=movie,
                tag=row['tag'],
                timestamp=row['timestamp']
            )

        # Import links
        links_df = pd.read_csv(os.path.join(csv_dir, 'links.csv'))
        links_df['tmdbId'].fillna(0, inplace=True)
        for _, row in links_df.iterrows():
            movie_id = row['movieId']
            try:
                movie = Movie.objects.get(movieId=movie_id)
            except Movie.DoesNotExist:
                print(f"Movie with movieId {movie_id} does not exist. Skipping...")
                continue 
            
            link = Link.objects.create(
                movieId=movie,
                imdbId=row['imdbId'],
                tmdbId=int(row['tmdbId'])
            )

        self.stdout.write('Data import complete.')
