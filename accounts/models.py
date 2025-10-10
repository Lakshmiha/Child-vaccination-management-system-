from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name = "Parent"
        verbose_name_plural = "Parents"


class Child(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ]
    
    parent = models.ForeignKey("Parent", on_delete=models.CASCADE, related_name='children')
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=5, blank=True)

    def __str__(self):
        return f"{self.name} (Child of {self.parent.user.username})"
    
    class Meta:
        verbose_name = "Child"
        verbose_name_plural = "Children"
        ordering = ['-date_of_birth']


class Hospital(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Hospital"
        verbose_name_plural = "Hospitals"
        ordering = ['name']


class Vaccine(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    recommended_age = models.CharField(max_length=50, blank=True, help_text="e.g., '0-6 months', '12-15 months'")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Vaccine"
        verbose_name_plural = "Vaccines"
        ordering = ['name']


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled')
    ]
    
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='appointments')
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='appointments')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='appointments')
    vaccine = models.ForeignKey(Vaccine, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, help_text="Additional notes or remarks")

    def __str__(self):
        return f"{self.child.name} - {self.hospital.name} on {self.date} at {self.time}"
    
    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"
        ordering = ['-date', '-time']
    
    @property
    def is_upcoming(self):
        """Check if appointment is in the future"""
        from datetime import datetime
        appointment_datetime = datetime.combine(self.date, self.time)
        return appointment_datetime > datetime.now() and self.status in ['Pending', 'Approved']
    
    @property
    def is_past(self):
        """Check if appointment is in the past"""
        from datetime import datetime
        appointment_datetime = datetime.combine(self.date, self.time)
        return appointment_datetime < datetime.now()