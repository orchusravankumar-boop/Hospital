from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from appointments.models import Appointment


# SIGNUP
def signup(request):

    if request.method == "POST":

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():

            return render(request, 'users/signup.html', {
                'error': 'Username already exists'
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        return redirect('/')

    return render(request, 'users/signup.html')


# LOGIN
def login_view(request):

    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            # BOTH doctor and patient go to home
            return redirect('/')

        else:

            return render(request, 'users/login.html', {
                'error': 'Invalid username or password'
            })

    return render(request, 'users/login.html')


# LOGOUT
def logout_view(request):

    logout(request)

    return redirect('/login/')


# MY APPOINTMENTS
@login_required
def my_appointments(request):

    appointments = Appointment.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'users/my_appointments.html',
        {
            'appointments': appointments
        }
    )