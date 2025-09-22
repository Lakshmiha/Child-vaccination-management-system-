from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ParentRegistrationForm,ChildForm
from .models import Parent,Child

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
    children = Child.objects.filter(parent=parent)
    return render(request, "accounts/parent_dashboard.html", {"parent": parent})

@login_required
def add_child(request):
    parent = Parent.objects.filter(user=request.user).first()
    if request.method == "POST":
        form = ChildForm(request.POST)
        if form.is_valid():
            child = form.save(commit=False)
            child.parent = parent
            child.save()
            messages.success(request, "Child added successfully.")
            return redirect('accounts:parent_dashboard')
    else:
        form = ChildForm()
    return render(request, "accounts/add_child.html", {"form": form})

@login_required
def view_children(request):
    parent = Parent.objects.filter(user=request.user).first()
    children = Child.objects.filter(parent=parent) if parent else []
    return render(request, "accounts/view_children.html", {"children": children})

@login_required
def edit_child(request, child_id):
    child = get_object_or_404(Child, id=child_id, parent__user=request.user)
    if request.method == "POST":
        form = ChildForm(request.POST, instance=child)
        if form.is_valid():
            form.save()
            messages.success(request, "Child details updated successfully.")
            return redirect('accounts:view_children')
    else:
        form = ChildForm(instance=child)
    return render(request, "accounts/edit_child.html", {"form": form})

@login_required
def delete_child(request, child_id):
    child = get_object_or_404(Child, id=child_id, parent__user=request.user)
    if request.method == "POST":
        child.delete()
        messages.success(request, "Child deleted successfully.")
        return redirect('accounts:view_children')
    return render(request, "accounts/delete_child.html", {"child": child})

