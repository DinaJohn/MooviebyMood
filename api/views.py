from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import render

def main_spa(request: HttpRequest) -> HttpResponse:
    return render(request, 'api/spa/index.html', {})

import json
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt

#login and logout
def login_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"error": "Invalid credentials"}, status=400)

def logout_view(request):
    logout(request)
    return JsonResponse({"success": True})

from django.views.decorators.http import require_http_methods
from .Recommend_functions import RecommendFunctions
from .models import Movie, Link
import requests

recommendation_system = RecommendFunctions()

# Finds the initial recomendation for the user
@require_http_methods(["POST"])
def mood_selection_content_recommendation(request):
    data = json.loads(request.body)
    user_id = data.get('userId')
    mood = data.get('mood')
    print(data)
    print("mood")
    if not mood:
        return JsonResponse({'status': 'error', 'message': 'Mood is required.'}, status=400)

    movie_title = recommendation_system.content_based_recommendations(mood, user_id)

    print(movie_title)
    
    if movie_title:
        movie = Movie.objects.get(title=movie_title)
        link = Link.objects.get(movieId=movie)
        tmbdlink = link.tmdbId
        details = fetch_movie_details(tmbdlink)
        return JsonResponse({'status': 'success', 'recommendation': movie_title, 'details': details})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON.'}, status=404)

# Processes user actions (Like, Dislike, Perfect) on recommendations and returns the next action or concludes the recommendation session.
@require_http_methods(["POST"])
def user_action_on_recommendation(request):
    if not request.body:
        return JsonResponse({'status': 'error', 'message': 'Empty request body'}, status=400)
    
    data = json.loads(request.body)
    action = data.get('action')
    movie_title = data.get('movieTitle')
    print(movie_title)
    user_id = data.get('userId')
    mood = data.get('mood') 

    if not all([action, movie_title, user_id, mood]):
        return JsonResponse({'status': 'error', 'message': 'Missing action, movie title, user ID or mood.'}, status=400)
    
    response = recommendation_system.process_user_action(movie_title, action, user_id, mood, data.get('type'))
    
    next_recommendation = response.get('next_recommendation')
    print(next_recommendation)
    message = response.get('message', '')
    if next_recommendation:
        movie = Movie.objects.get(title=next_recommendation)
        link = Link.objects.get(movieId=movie)
        tmbdlink = link.tmdbId
        details = fetch_movie_details(tmbdlink)
        return JsonResponse({'status': 'success', 'next_recommendation': next_recommendation, 'message': message, 'details': details})
    else:
        return JsonResponse({'status': 'success', 'next_recommendation': None, 'message': message})
    
# fetches movie details for the recommended movie
@csrf_exempt
def fetch_movie_details(movie_id):
    print(movie_id)
    if not movie_id:
        return JsonResponse({'status': 'error', 'message': 'Movie ID is required.'}, status=400)
    
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?append_to_response=reviews%2Cvideos&language=en-US"
    print(url)

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJiMmM2NjBlYWY0NDk4OWM3ZjYzZDczNDc3OTY3MjQ4ZiIsInN1YiI6IjY1ZjgzZTA0ZWI3OWMyMDE3YzU1OGNlYyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.5OnVpsoH-zHGn0EqsC8_WA5lIfncS0dbchlklN1Oq00"
    }

    try:
        response = requests.get(url, headers=headers)
        print(response.text)
        return response.json()
    except requests.exceptions.RequestException as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

# resets the system once the user is satisfied with the recommendations
@require_http_methods(["POST"])
def refresh_recommendations(request):
    recommendation_system.refresh_data()
    return JsonResponse({'status': 'success', 'message': 'Recommendations refreshed successfully.'})