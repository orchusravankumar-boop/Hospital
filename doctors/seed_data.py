from django.contrib.auth.models import User

from doctors.models import Doctor


DEFAULT_DOCTORS = [
    ("DOC102", "Aarav Mehta", "General Physician", "9001002001", "G-101", "9:00 AM - 1:00 PM"),
    ("DOC103", "Ishita Rao", "Cardiology", "9001002002", "C-214", "10:30 AM - 2:30 PM"),
    ("DOC104", "Kabir Nanda", "Neurology", "9001002003", "N-307", "4:00 PM - 8:00 PM"),
    ("DOC105", "Nisha Varma", "Orthopedics", "9001002004", "O-118", "11:00 AM - 3:00 PM"),
    ("DOC106", "Rohan Kapoor", "Dermatology", "9001002005", "D-225", "2:00 PM - 6:00 PM"),
    ("DOC107", "Megha Iyer", "Pediatrics", "9001002006", "P-109", "8:30 AM - 12:30 PM"),
    ("DOC108", "Aditya Sen", "ENT", "9001002007", "E-316", "5:00 PM - 9:00 PM"),
    ("DOC109", "Kritika Shah", "Radiology", "9001002008", "R-402", "9:30 AM - 1:30 PM"),
    ("DOC110", "Vivaan Joshi", "Dental Care", "9001002009", "DC-121", "3:00 PM - 7:00 PM"),
    ("DOC111", "Saanvi Kulkarni", "Eye Specialist", "9001002010", "V-208", "10:00 AM - 4:00 PM"),
]


def seed_default_doctors_and_staff():
    from appointments.models import Appointment

    doctor_ids = [doctor[0] for doctor in DEFAULT_DOCTORS]

    created_doctors = 0
    updated_doctors = 0
    created_users = 0
    updated_users = 0

    for doctor_data in DEFAULT_DOCTORS:
        doctor_id, name, specialization, phone, room_number, op_timings = doctor_data

        doctor = Doctor.objects.filter(doctor_id=doctor_id).first()
        legacy_doctors = Doctor.objects.filter(
            name=name,
            specialization=specialization,
        )
        if doctor:
            legacy_doctors = legacy_doctors.exclude(id=doctor.id)
        else:
            doctor = legacy_doctors.first()

        doctor_created = doctor is None

        if doctor_created:
            doctor = Doctor(doctor_id=doctor_id)

        doctor.doctor_id = doctor_id
        doctor.name = name
        doctor.specialization = specialization
        doctor.phone = phone
        doctor.room_number = room_number
        doctor.op_timings = op_timings
        doctor.save()

        for legacy_doctor in legacy_doctors.exclude(id=doctor.id):
            Appointment.objects.filter(doctor=legacy_doctor).update(doctor=doctor)
            legacy_doctor.delete()

        first_name = name.split()[0]
        last_name = " ".join(name.split()[1:])
        user, user_created = User.objects.get_or_create(
            username=doctor_id,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "is_staff": True,
            },
        )
        user.first_name = first_name
        user.last_name = last_name
        user.is_staff = True
        user.set_password(f"{first_name}@123")
        user.save()

        created_doctors += int(doctor_created)
        updated_doctors += int(not doctor_created)
        created_users += int(user_created)
        updated_users += int(not user_created)

    fallback_doctor = Doctor.objects.filter(doctor_id=doctor_ids[0]).first()
    extra_doctors = Doctor.objects.exclude(doctor_id__in=doctor_ids)

    if fallback_doctor:
        Appointment.objects.filter(doctor__in=extra_doctors).update(
            doctor=fallback_doctor
        )

    deleted_doctors, _ = extra_doctors.delete()

    return {
        "deleted_doctors": deleted_doctors,
        "created_doctors": created_doctors,
        "updated_doctors": updated_doctors,
        "created_users": created_users,
        "updated_users": updated_users,
    }
