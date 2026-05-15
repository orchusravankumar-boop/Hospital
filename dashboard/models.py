from django.db import models

class Patient(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField(default=0)
    disease = models.CharField(max_length=200)

    def __str__(self):
        return self.name