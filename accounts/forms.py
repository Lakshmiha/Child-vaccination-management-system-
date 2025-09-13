from django import forms
from django.contrib.auth.models import User
from .models import Parent

class ParentRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Parent
        fields = ['phone_number', 'address']

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        parent = Parent(
            user=user,
            phone_number=self.cleaned_data['phone_number'],
            address=self.cleaned_data['address']
        )
        if commit:
            user.save()
            parent.save()
        return parent
