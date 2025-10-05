from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.user.username

class Child(models.Model):
    parent = models.ForeignKey("Parent", on_delete=models.CASCADE, related_name='children')
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]
    )
    blood_group = models.CharField(max_length=5, blank=True)

    def __str__(self):
        return self.name


class Hospital(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=20,unique=True)
    email = models.EmailField(unique=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    

class Appointment(models.Model):
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'),('Approved','Approved'),('Completed', 'Completed'),('Cancelled','Cancelled')],
        default='Pending'
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.child.name} - {self.hospital.name} ({self.date})"