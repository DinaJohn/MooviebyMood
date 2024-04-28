# Models created to store information about Movies, Ratings, Tags and Links

from django.db import models

class Movie(models.Model):
    movieId = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    genres = models.TextField()

class Rating(models.Model):
    userId = models.IntegerField()
    movieId = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.FloatField()
    timestamp = models.DateTimeField()

class Tag(models.Model):
    userId = models.IntegerField()
    movieId = models.ForeignKey(Movie, on_delete=models.CASCADE)
    tag = models.CharField(max_length=255)
    timestamp = models.DateTimeField()

class Link(models.Model):
    movieId = models.OneToOneField(Movie, on_delete=models.CASCADE, primary_key=True)
    imdbId = models.CharField(max_length=255)
    tmdbId = models.IntegerField()