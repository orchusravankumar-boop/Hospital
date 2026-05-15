from django.shortcuts import render
from appointments.models import Appointment


def home(request):

    appointments = None

    if request.user.is_authenticated and not request.user.is_staff:

        appointments = Appointment.objects.filter(
            user=request.user
        ).order_by('-created_at')

    return render(
        request,
        'marketing/marketing.html',
        {
            'appointments': appointments
        }
    )