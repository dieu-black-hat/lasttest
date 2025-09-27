from django.db import models

class Registration(models.Model):
    first_name = models.CharField(max_length=30)
    second_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    class_level = models.CharField(max_length=20)
    faculty = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)  # Removed the validators
    password = models.CharField(max_length=128)  # Store hashed password

    def __str__(self):
        return f"{self.first_name} {self.second_name} - {self.email}"