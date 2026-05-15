from django.db import models
from django.contrib.auth.models import User


class Appointment(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True
    )

    patient_name = models.CharField(max_length=200)

    phone = models.CharField(max_length=20)

    age = models.IntegerField()

    doctor = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.CASCADE
    )

    appointment_status = models.CharField(
        max_length=100,
        default="Pending"
    )

    # NEW FIELDS

    weight = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    temperature = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    diagnosis = models.TextField(
        blank=True,
        null=True
    )

    medicines = models.TextField(
        blank=True,
        null=True
    )

    doctor_notes = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"{self.patient_name} - {self.doctor.name}"