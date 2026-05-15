from django.shortcuts import render
from doctors.models import Doctor


def ai_chat(request):

    symptom = request.GET.get('symptom', '').lower()

    doctor = None

    if "heart" in symptom or "chest pain" in symptom:
        doctor = Doctor.objects.filter(
            specialization__icontains="Cardiologist"
        ).first()

    elif "skin" in symptom or "pimple" in symptom:
        doctor = Doctor.objects.filter(
            specialization__icontains="Dermatologist"
        ).first()

    elif "eye" in symptom:
        doctor = Doctor.objects.filter(
            specialization__icontains="Eye"
        ).first()

    elif "bone" in symptom or "joint" in symptom:
        doctor = Doctor.objects.filter(
            specialization__icontains="Orthopedic"
        ).first()

    else:
        doctor = Doctor.objects.first()

    return render(request, 'dashboard/ai_result.html', {
        'symptom': symptom,
        'doctor': doctor
    })