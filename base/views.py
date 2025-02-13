from django.shortcuts import render

# Create your views here.

def dashboard(request):
    return render(request, 'base/dashboard.html')

def signin(request):
    return render(request, 'base/sign-in.html')
