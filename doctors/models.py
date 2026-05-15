from django.db import models


class Doctor(models.Model):

    doctor_id = models.CharField(
    max_length=20,
    unique=True,
    null=True,
    blank=True
)
    

    name = models.CharField(max_length=100)

    specialization = models.CharField(max_length=100)

    phone = models.CharField(max_length=15)

    room_number = models.CharField(max_length=20)

    op_timings = models.CharField(max_length=100)

    def __str__(self):

        return self.name