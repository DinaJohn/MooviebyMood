from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponse

from .views import main_spa, mood_selection_content_recommendation, login_view, logout_view, user_action_on_recommendation, refresh_recommendations, fetch_movie_details

urlpatterns = [
    path('', main_spa),
    path('api/login/', login_view, name='login'),
    path('api/logout/', logout_view, name='logout'),
    path('api/mood_selection_content_recommendation/', mood_selection_content_recommendation, name='select_mood_with_initial_recommendations'),
    path('api/user_action_on_recommendation/', user_action_on_recommendation, name='user_action_on_recommendation'),
    path('api/refresh_recommendations/', refresh_recommendations, name='refresh_recommendations'),
    path('api/fetch_movie_details/', fetch_movie_details, name='fetch_movie_details'),
]

