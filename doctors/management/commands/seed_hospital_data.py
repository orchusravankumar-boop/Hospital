from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from doctors.models import Doctor


class Command(BaseCommand):
    help = "Seed default doctors and doctor staff users."

    doctors = [
        ("DOC001", "Aarav Mehta", "General Physician", "9001002001", "G-101", "9:00 AM - 1:00 PM"),
        ("DOC002", "Ishita Rao", "Cardiology", "9001002002", "C-214", "10:30 AM - 2:30 PM"),
        ("DOC003", "Kabir Nanda", "Neurology", "9001002003", "N-307", "4:00 PM - 8:00 PM"),
        ("DOC004", "Nisha Varma", "Orthopedics", "9001002004", "O-118", "11:00 AM - 3:00 PM"),
        ("DOC005", "Rohan Kapoor", "Dermatology", "9001002005", "D-225", "2:00 PM - 6:00 PM"),
        ("DOC006", "Megha Iyer", "Pediatrics", "9001002006", "P-109", "8:30 AM - 12:30 PM"),
        ("DOC007", "Aditya Sen", "ENT", "9001002007", "E-316", "5:00 PM - 9:00 PM"),
        ("DOC008", "Kritika Shah", "Radiology", "9001002008", "R-402", "9:30 AM - 1:30 PM"),
        ("DOC009", "Vivaan Joshi", "Dental Care", "9001002009", "DC-121", "3:00 PM - 7:00 PM"),
        ("DOC010", "Saanvi Kulkarni", "Eye Specialist", "9001002010", "V-208", "10:00 AM - 4:00 PM"),
    ]

    def handle(self, *args, **options):
        created_doctors = 0
        updated_doctors = 0
        created_users = 0
        updated_users = 0

        for index, doctor_data in enumerate(self.doctors, start=102):
            doctor_id, name, specialization, phone, room_number, op_timings = doctor_data
            _, doctor_created = Doctor.objects.update_or_create(
                doctor_id=doctor_id,
                defaults={
                    "name": name,
                    "specialization": specialization,
                    "phone": phone,
                    "room_number": room_number,
                    "op_timings": op_timings,
                },
            )

            first_name = name.split()[0]
            last_name = " ".join(name.split()[1:])
            password = f"{first_name}@123"
            username = f"DOC{index}"

            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "is_staff": True,
                },
            )
            user.first_name = first_name
            user.last_name = last_name
            user.is_staff = True
            user.set_password(password)
            user.save()

            created_doctors += int(doctor_created)
            updated_doctors += int(not doctor_created)
            created_users += int(user_created)
            updated_users += int(not user_created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Doctors created={created_doctors}, updated={updated_doctors}; "
                f"staff users created={created_users}, updated={updated_users}"
            )
        )
