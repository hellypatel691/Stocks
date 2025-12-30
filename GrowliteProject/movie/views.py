from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def about(request):
    return HttpResponse('<h1>Welcome to About Page</h1>')

def home(request):
    searchTerm = request.GET.get('searchMovie')
    return render(request, 'movie/home.html', 
    {'searchTerm':searchTerm})

def signup(request):
    email = request.GET.get('email')
    return render(request, 'movie/signup.html', {'email':email})


