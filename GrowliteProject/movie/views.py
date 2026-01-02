from django.shortcuts import render

from .models import Movie

# Create your views here.
from django.http import HttpResponse

def about(request):
    return HttpResponse('<h1>Welcome to About Page</h1>')

# def home(request):
#     searchTerm = request.GET.get('searchMovie')
#     movies = Movie.objects.all()
#     searchTerm = request.GET.get('searchMovie')
#     return render(request, 'movie/home.html',
#       {'searchTerm':searchTerm, 'movies': movies})

def home(request):
    searchTerm = request.GET.get('searchMovie')
    if searchTerm:
        movies =Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()
    return render(request, 'movie/home.html',
      {'searchTerm':searchTerm, 'movies': movies})


def signup(request):
    email = request.GET.get('email')
    return render(request, 'movie/signup.html', {'email':email})


