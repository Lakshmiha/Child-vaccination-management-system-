from django import forms
from django.contrib.auth.models import User
from .models import Parent,Child
from django.core.exceptions import ValidationError
from django.forms.widgets import DateInput

class ParentRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput, required=True)

    class Meta:
        model = Parent
        fields = ['phone_number', 'address']  # Parent-specific fields

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
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
        # create User then Parent
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
            'date_of_birth': DateInput(attrs={'type': 'date'}),
        }