from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms.widgets import DateInput, TimeInput
from .models import Parent, Child, Hospital, Appointment, Vaccine,Inventory
from datetime import date


class ParentRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput, required=True)

    class Meta:
        model = Parent
        fields = ['phone_number', 'address']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            existing_user = User.objects.get(username=username)
            if hasattr(existing_user, 'hospital'):
                raise ValidationError("Username already taken.")
        return username

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError("Passwords do not match.")
        return cleaned

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1']
        )
        parent = Parent(
            user=user,
            phone_number=self.cleaned_data.get('phone_number', ''),
            address=self.cleaned_data.get('address', '')
        )
        if commit:
            user.save()
            parent.save()
        return parent


class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['name', 'date_of_birth', 'gender', 'blood_group']
        widgets = {
            'date_of_birth': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'blood_group': forms.TextInput(attrs={'class': 'form-control'}),
        }


class HospitalRegisterForm(forms.ModelForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Hospital
        fields = ['name', 'address', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            existing_user = User.objects.get(username=username)
            if hasattr(existing_user, 'parent'):
                raise forms.ValidationError("This username is already registered as a Parent.")
            raise forms.ValidationError("Username already taken.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        
        email_check = cleaned_data.get('email')
        if email_check and Hospital.objects.filter(email=email_check).exists():
            raise forms.ValidationError("This email is already registered to another hospital.")
        return cleaned_data

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1']
        )
        user.is_active = False

        hospital = Hospital(
            user=user,
            name=self.cleaned_data['name'],
            address=self.cleaned_data['address'],
            phone=self.cleaned_data['phone'],
            email=self.cleaned_data['email'],
            approved=False
        )
        if commit:
            user.save()
            hospital.save()
        return hospital


# --- In accounts/forms.py ---

class AppointmentForm(forms.ModelForm):
    # ... (Meta and __init__ methods unchanged for now)

    def clean(self):
        cleaned_data = super().clean()
        hospital = cleaned_data.get('hospital')
        vaccine = cleaned_data.get('vaccine')
        date = cleaned_data.get('date')

        # Existing clean_date validation (important to keep)
        # ...

        # **New Inventory Validation Logic**
        if hospital and vaccine:
            try:
                inventory = Inventory.objects.get(hospital=hospital, vaccine=vaccine)
                if inventory.stock_quantity <= 0:
                    self.add_error(
                        'vaccine',
                        f"{vaccine.name} is currently out of stock at {hospital.name}."
                    )
            except Inventory.DoesNotExist:
                # If no inventory record exists, assume out of stock for booking purposes
                self.add_error(
                    'vaccine',
                    f"{vaccine.name} inventory data is unavailable at {hospital.name} (Out of stock or not offered)."
                )

        return cleaned_data
    
class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['name', 'date_of_birth', 'gender', 'blood_group']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'blood_group': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Browser-level cap
        self.fields['date_of_birth'].widget.attrs['max'] = date.today().isoformat()

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob and dob > date.today():
            raise forms.ValidationError("Date of birth cannot be in the future.")
        return dob