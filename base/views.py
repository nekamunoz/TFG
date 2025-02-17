from django.shortcuts import render

# Create your views here.

def dashboard(request):
    return render(request, 'dashboard.html')

def signin(request):
    return render(request, 'sign-in.html')

def signup(request):
    return render(request, 'sign-up.html')

def profile(request):
    return render(request, 'profile.html')


def main(request):
    return render(request, 'main.html')