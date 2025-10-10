from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms.widgets import DateInput, TimeInput
from .models import Parent, Child, Hospital, Appointment, Vaccine
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


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['child', 'hospital', 'vaccine', 'date', 'time', 'notes']
        widgets = {
            'date': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any additional information...'}),
        }

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop('parent', None)
        super().__init__(*args, **kwargs)
        
        # Only show approved hospitals
        self.fields['hospital'].queryset = Hospital.objects.filter(approved=True)
        self.fields['hospital'].widget.attrs.update({'class': 'form-control'})
        
        # Only show this parent's children
        if parent:
            self.fields['child'].queryset = Child.objects.filter(parent=parent)
        else:
            self.fields['child'].queryset = Child.objects.none()
        
        self.fields['child'].widget.attrs.update({'class': 'form-control'})
        
        # Make vaccine optional
        self.fields['vaccine'].required = False
        self.fields['vaccine'].queryset = Vaccine.objects.all()
        self.fields['vaccine'].widget.attrs.update({'class': 'form-control'})
        
        # Make notes optional
        self.fields['notes'].required = False

    def clean_date(self):
        """Validate that appointment date is not in the past"""
        appointment_date = self.cleaned_data.get('date')
        if appointment_date and appointment_date < date.today():
            raise forms.ValidationError("Appointment date cannot be in the past.")
        return appointment_date