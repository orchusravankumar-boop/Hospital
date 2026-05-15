from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from appointments.models import Appointment
from doctors.seed_data import seed_default_doctors_and_staff


def normalize_doctor_username(username):
    normalized_username = username.strip().upper()

    if normalized_username.isdigit():

        doctor_number = int(normalized_username)

        if 1 <= doctor_number <= 10:

            return f"DOC{doctor_number + 101}"

        return f"DOC{doctor_number}"

    if normalized_username.startswith("DOC") and normalized_username[3:].isdigit():

        doctor_number = int(normalized_username[3:])

        if 1 <= doctor_number <= 10:

            return f"DOC{doctor_number + 101}"

    return normalized_username


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

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password')

        normalized_username = normalize_doctor_username(username)

        if normalized_username.startswith("DOC"):

            seed_default_doctors_and_staff()

        user = authenticate(
            request,
            username=normalized_username,
            password=password
        )

        if user is not None:

            login(request, user)

            if user.is_staff and user.username.startswith("DOC"):

                return redirect('/doctors/dashboard/')

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
