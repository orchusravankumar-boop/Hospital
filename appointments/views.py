import json
import resend
from django.conf import settings
from django.shortcuts import render
from google import genai
from doctors.models import Doctor
from appointments.models import Appointment


def fallback_symptom_analysis(symptom):
    if any(word in symptom for word in ['heart', 'chest pain', 'bp', 'blood pressure', 'heartbeat']):
        return "Cardiology", "Your symptoms may be related to heart problems. Please consult a Cardiologist for proper evaluation."

    if any(word in symptom for word in ['headache', 'migraine', 'brain', 'dizziness', 'seizure']):
        return "Neurology", "Your symptoms appear related to neurological issues. Please consult a Neurologist for further diagnosis."

    if any(word in symptom for word in ['bone', 'joint', 'fracture', 'back pain', 'knee pain']):
        return "Orthopedics", "Your symptoms may be related to bones or joints. Please consult an Orthopedic specialist."

    if any(word in symptom for word in ['skin', 'pimple', 'rash', 'itching', 'acne', 'allergy']):
        return "Dermatology", "Your symptoms appear related to skin conditions. Please consult a Dermatologist."

    if any(word in symptom for word in ['baby', 'child', 'kids', 'child fever', 'baby cold']):
        return "Pediatrics", "Your symptoms appear related to child healthcare. Please consult a Pediatrician."

    if any(word in symptom for word in ['ear', 'nose', 'throat', 'sinus', 'ear pain']):
        return "ENT", "Your symptoms may be related to ear, nose or throat conditions. Please consult an ENT specialist."

    if any(word in symptom for word in ['scan', 'mri', 'xray', 'ct scan']):
        return "Radiology", "Diagnostic imaging consultation is recommended. Please consult the Radiology department."

    if any(word in symptom for word in ['accident', 'trauma', 'bleeding', 'emergency']):
        return "Emergency Care", "Your symptoms indicate emergency care is needed. Please immediately consult Emergency specialists."

    if any(word in symptom for word in ['tooth', 'teeth', 'gum', 'cavity', 'dental']):
        return "Dental Care", "Your symptoms appear related to dental problems. Please consult a Dental specialist."

    if any(word in symptom for word in ['eye', 'vision', 'blurred vision']):
        return "Eye Specialist", "Your symptoms indicate eye-related issues. Please consult an Eye Specialist."

    if any(word in symptom for word in ['fever', 'cold', 'cough', 'infection', 'body ache', 'fatigue', 'weakness', 'sore throat', 'nausea']):
        return "General Physician", "Your symptoms may be related to fever or infection. Please consult a General Physician."

    return "General Physician", "General medical consultation is recommended based on the provided symptoms."


def clean_gemini_json(response_text):
    cleaned_text = response_text.strip()

    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text.replace("```json", "", 1).strip()

    if cleaned_text.startswith("```"):
        cleaned_text = cleaned_text.replace("```", "", 1).strip()

    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[:-3].strip()

    return json.loads(cleaned_text)


def gemini_symptom_analysis(symptom, doctors):
    specializations = list(
        doctors.values_list('specialization', flat=True).distinct()
    )

    fallback_department, fallback_explanation = fallback_symptom_analysis(symptom)

    if not settings.GEMINI_API_KEY or not specializations:
        return fallback_department, fallback_explanation

    prompt = f"""
You are assisting a hospital appointment booking page.

User symptoms:
{symptom}

Available doctor specializations in this hospital database:
{", ".join(specializations)}

Task:
1. Explain the user's symptoms in simple, careful language.
2. Choose exactly one specialization from the available specializations list.
3. Do not diagnose the user. Do not claim certainty.
4. If symptoms sound urgent, include a short emergency warning in the explanation.

Return only valid JSON in this exact format:
{{
  "specialization": "one exact specialization from the available list",
  "explanation": "short patient-friendly explanation"
}}
"""

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
        )
        analysis = clean_gemini_json(response.text)
        gemini_specialization = analysis.get("specialization", "").strip()
        gemini_explanation = analysis.get("explanation", "").strip()

        if gemini_specialization in specializations and gemini_explanation:
            return gemini_specialization, gemini_explanation

    except Exception as error:
        print("Gemini symptom analysis failed:", error)

    return fallback_department, fallback_explanation


# APPOINTMENT PAGE
def appointment_page(request):
    symptom = request.GET.get('symptom', '').lower()

    recommended_department = None
    explanation = ""

    doctors = Doctor.objects.all()
    recommended_doctors = doctors

    if symptom == "":
        return render(
            request,
            'appointments/appointments.html',
            {
                'ai_mode': False,
                'doctor': None,
                'recommended_doctors': None,
                'recommended_department': None,
                'selected_doctor': None,
                'doctors': doctors,
                'symptom': '',
                'explanation': ''
            }
        )

    recommended_department, explanation = gemini_symptom_analysis(
        symptom,
        doctors
    )

    recommended_doctors = Doctor.objects.filter(
        specialization__icontains=recommended_department
    )

    if not recommended_doctors.exists():
        recommended_doctors = doctors

    return render(request, 'appointments/appointments.html', {
        'ai_mode': True,
        'doctor': None,
        'recommended_doctors': recommended_doctors,
        'recommended_department': recommended_department,
        'selected_doctor': recommended_doctors.first(),
        'doctors': doctors,
        'symptom': symptom,
        'explanation': explanation
    })


def confirm_appointment(request):
    if request.method == "POST":
        doctor_id = request.POST.get('doctor')
        patient_name = request.POST.get('patient_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        age = request.POST.get('age')

        doctor = Doctor.objects.get(id=doctor_id)

        Appointment.objects.create(
            user=request.user if request.user.is_authenticated else None,
            patient_name=patient_name,
            phone=phone,
            age=age,
            doctor=doctor,
            appointment_status="Pending"
        )

        resend.api_key = settings.RESEND_API_KEY

        email_status = "sent"

        try:
            resend.Emails.send({
                "from": "Sravan Hospital <onboarding@resend.dev>",
                "to": [email],
                "subject": "Appointment Confirmation - Sravan Hospital",
                "html": f"""
                    <h1>Appointment Confirmed</h1>
                    <p>Hello {patient_name},</p>
                    <p>Your appointment has been successfully booked.</p>

                    <h3>Doctor Details</h3>
                    <ul>
                        <li><strong>Doctor:</strong> Dr. {doctor.name}</li>
                        <li><strong>Specialization:</strong> {doctor.specialization}</li>
                        <li><strong>OP Timings:</strong> {doctor.op_timings}</li>
                        <li><strong>Room Number:</strong> {doctor.room_number}</li>
                    </ul>

                    <p>Thank you for choosing Sravan Hospital.</p>
                """
            })
        except Exception as error:
            email_status = "failed"
            print("Appointment email failed:", error)

        return render(request, 'appointments/success.html', {
            'doctor': doctor,
            'patient_name': patient_name,
            'email_status': email_status
        })

    return render(request, 'appointments/success.html')
