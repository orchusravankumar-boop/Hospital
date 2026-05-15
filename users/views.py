from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from appointments.models import Appointment
from doctors.models import Doctor
from doctors.seed_data import seed_default_doctors_and_staff
from patients.models import Patient


def save_patient_profile(user):
    if user.is_staff:
        return None

    patient, _ = Patient.objects.update_or_create(
        user=user,
        defaults={
            'username': user.username,
            'name': user.get_full_name() or user.username,
            'email': user.email,
        }
    )

    return patient


def record_patient_login(user):
    patient = save_patient_profile(user)

    if not patient:
        return

    patient.last_login_at = timezone.now()
    patient.login_count += 1
    patient.save(update_fields=['last_login_at', 'login_count'])


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


def is_doctor_login_username(username):
    normalized_username = username.strip().upper()

    return (
        normalized_username.isdigit()
        or (
            normalized_username.startswith("DOC")
            and normalized_username[3:].isdigit()
        )
    )


def authenticate_doctor_with_password_variants(username, password):
    user = User.objects.filter(
        username=username,
        is_staff=True,
    ).first()

    doctor = Doctor.objects.filter(
        doctor_id=username
    ).first()

    if not user or not doctor:

        return None

    first_name = doctor.name.split()[0]
    compact_name = doctor.name.replace(" ", "")
    allowed_passwords = {
        f"{first_name}@123",
        f"{first_name.lower()}@123",
        f"{first_name.upper()}@123",
        f"{compact_name}@123",
        f"{compact_name.lower()}@123",
    }

    if password in allowed_passwords:

        user.set_password(f"{first_name}@123")
        user.save()

        return user

    return None


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
        record_patient_login(user)

        return redirect('/')

    return render(request, 'users/signup.html')


# LOGIN
def login_view(request):

    if request.method == "POST":

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is None and not is_doctor_login_username(username):

            existing_user = User.objects.filter(
                username__iexact=username
            ).first()

            if existing_user:

                user = authenticate(
                    request,
                    username=existing_user.username,
                    password=password
                )

        if user is None and is_doctor_login_username(username):

            seed_default_doctors_and_staff()
            normalized_username = normalize_doctor_username(username)

            user = authenticate(
                request,
                username=normalized_username,
                password=password
            )

            if user is None:

                user = authenticate_doctor_with_password_variants(
                    normalized_username,
                    password
                )

        if user is not None:

            login(request, user)

            if user.is_staff and user.username.startswith("DOC"):

                return redirect('/doctors/dashboard/')

            record_patient_login(user)

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
