from django.conf import settings
from django.db import models

class Patient(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='patient_profile',
    )
    username = models.CharField(max_length=150, blank=True)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField()
    last_login_at = models.DateTimeField(blank=True, null=True)
    login_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
