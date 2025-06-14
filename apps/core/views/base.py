from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required  

from ..forms import CustomRegistrationForm

def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save() 
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomRegistrationForm()

    return render(request, 'sign-up.html', {'form': form})

def signin(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard') 
        else:
            messages.error(request, 'Invalid username or password', extra_tags='alert alert-danger text-center')
            return render(request, 'sign-in.html')
    else:
        if len(request.META["QUERY_STRING"]) > 0:
            messages.error(request, 'You need to log in first', extra_tags='alert alert-danger text-center')
        
    return render(request, 'sign-in.html')

def signout(request):
    logout(request)  
    return redirect('sign-in')

@login_required
def profile(request):
    context = {
        'user': request.user
    }
    return render(request, 'profile.html', context)