from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from doctors.models import Doctor
from appointments.models import Appointment


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

    doctor = Doctor.objects.filter(
        doctor_id=request.user.username
    ).first()

    status_filter = request.GET.get('status')

    appointments = Appointment.objects.filter(
        doctor=doctor
    )

    if status_filter and status_filter != "All":

        appointments = appointments.filter(
            appointment_status=status_filter
        )

    appointments = appointments.order_by('-created_at')

    return render(
        request,
        'doctors/dashboard.html',
        {
            'appointments': appointments,
            'doctor': doctor,
            'selected_status': status_filter
        }
    )


# UPDATE STATUS + MEDICAL DETAILS
@login_required
def update_status(request, appointment_id):

    if not request.user.is_staff:

        return redirect('/')

    appointment = Appointment.objects.get(
        id=appointment_id
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