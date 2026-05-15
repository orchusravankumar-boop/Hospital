from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from doctors.models import Doctor
from doctors.seed_data import seed_default_doctors_and_staff
from appointments.models import Appointment


def get_doctor_for_user(user):
    doctor = Doctor.objects.filter(
        doctor_id=user.username
    ).first()

    if doctor:
        return doctor

    if user.username.startswith("DOC"):

        seed_default_doctors_and_staff()

        doctor = Doctor.objects.filter(
            doctor_id=user.username
        ).first()

        if doctor:
            return doctor

    full_name = user.get_full_name().strip()

    if full_name:
        doctor = Doctor.objects.filter(
            name__iexact=full_name
        ).first()

    return doctor


def get_related_doctors(doctor):
    if not doctor:

        return Doctor.objects.none()

    return Doctor.objects.filter(
        Q(id=doctor.id)
        | Q(
            name__iexact=doctor.name,
            specialization__iexact=doctor.specialization
        )
    )


# DOCTOR LIST
def doc_list(request):

    doctors = Doctor.objects.all()

    return render(
        request,
        'doctors/doc_list.html',
        {
            'doctors': doctors
        }
    )


# DOCTOR DASHBOARD
@login_required
def doctor_dashboard(request):

    if not request.user.is_staff:

        return redirect('/')

    doctor = get_doctor_for_user(request.user)

    status_filter = request.GET.get('status')
    selected_date = request.GET.get('date')

    appointments = Appointment.objects.none()

    if doctor:

        related_doctors = get_related_doctors(doctor)

        appointments = Appointment.objects.filter(
            doctor__in=related_doctors
        )

        if status_filter and status_filter != "All":

            appointments = appointments.filter(
                appointment_status=status_filter
            )

        if selected_date:

            appointments = appointments.filter(
                appointment_date=selected_date
            )

        appointments = appointments.order_by('-created_at')

    return render(
        request,
        'doctors/dashboard.html',
        {
            'appointments': appointments,
            'doctor': doctor,
            'doctor_name': doctor.name if doctor else request.user.username,
            'selected_status': status_filter,
            'selected_date': selected_date
        }
    )


# UPDATE STATUS + MEDICAL DETAILS
@login_required
def update_status(request, appointment_id):

    if not request.user.is_staff:

        return redirect('/')

    doctor = get_doctor_for_user(request.user)
    related_doctors = get_related_doctors(doctor)

    appointment = Appointment.objects.get(
        id=appointment_id,
        doctor__in=related_doctors
    )

    if request.method == "POST":

        appointment.appointment_status = request.POST.get('status')

        appointment.weight = request.POST.get('weight')

        appointment.temperature = request.POST.get('temperature')

        appointment.diagnosis = request.POST.get('diagnosis')

        appointment.medicines = request.POST.get('medicines')

        appointment.doctor_notes = request.POST.get('doctor_notes')

        appointment.save()

    return redirect('/doctors/dashboard/')
