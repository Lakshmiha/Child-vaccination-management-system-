from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ParentRegistrationForm
from .models import Parent

def home(request):
    """Root URL: redirect to dashboard if logged in, else to login"""
    if request.user.is_authenticated:
        return redirect('accounts:parent_dashboard')
    return redirect('accounts:parent_login')


def parent_register(request):
    if request.method == "POST":
        form = ParentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. Please log in.")
            return redirect("accounts:parent_login")   # ✅ fixed typo here
        else:
            return render(request, "accounts/parent_register.html", {"form": form})
    else:
        form = ParentRegistrationForm()
    return render(request, "accounts/parent_register.html", {"form": form})


def parent_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful.")
            return redirect('accounts:parent_dashboard')  # ✅ goes to /dashboard/
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, "accounts/parent_login.html")
    return render(request, "accounts/parent_login.html")


def parent_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('accounts:parent_login')


@login_required
def parent_dashboard(request):
    parent = Parent.objects.filter(user=request.user).first()
    return render(request, "accounts/parent_dashboard.html", {"parent": parent})
