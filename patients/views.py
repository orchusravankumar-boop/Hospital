from django.shortcuts import render, get_object_or_404, redirect
from .models import Patient

def patient_list(request):

    patients = Patient.objects.all()

    return render(
        request,
        'patients/list.html',
        {'patients': patients}
    )


def patient_edit(request, pk):

    patient = get_object_or_404(Patient, pk=pk)

    if request.method == 'POST':

        patient.name = request.POST.get('name')
        patient.phone = request.POST.get('phone')
        patient.email = request.POST.get('email')

        patient.save()

        return redirect('patient_list')

    return render(
        request,
        'patients/patient_edit.html',
        {'patient': patient}
    )