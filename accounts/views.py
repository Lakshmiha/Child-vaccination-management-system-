from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from .forms import ParentRegistrationForm,ChildForm
from .models import Parent,Child
from .forms import HospitalRegisterForm
from .models import Hospital
from .models import Appointment,Hospital
from .forms import AppointmentForm

def home(request):  
    """Root URL: redirect to dashboard if logged in, else to login"""
    #if request.user.is_authenticated:
        #return redirect('accounts:parent_dashboard')
    return render(request,'accounts/home.html')


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
    try:
        parent = Parent.objects.filter(user=request.user).first()
    except Parent.DoesNotExist:
        parent=None
    children = Child.objects.filter(parent=parent)
    return render(request, "accounts/parent_dashboard.html", {"parent": parent,"children":children})

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


def hospital_register(request):
    if request.method == "POST":
        form = HospitalRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Hospital registered — awaiting admin approval.")
            return redirect('accounts:hospital_login')
        
        else:
            for field,errors in form.errors.items():
                for error in errors:
                    messages.error(request,f"Error in {field}:{error}")

    else:
        form = HospitalRegisterForm()
    return render(request, 'accounts/hospital_register.html', {'form': form})

#def hospital_login(request):
    #if request.method == "POST":
        #username = request.POST.get('username')
        #password = request.POST.get('password')
        #user = authenticate(request, username=username, password=password)
        #if user is not None:
            # check hospital profile and approval
            #try:
                #hospital = user.hospital
            #except Hospital.DoesNotExist:
                #messages.error(request, "No hospital profile found for this account.")
                #return redirect('accounts:hospital_login')

            #if not hospital.approved:
                #messages.warning(request, "Your hospital registration is pending admin approval.")
                #return redirect('accounts:hospital_login')

            #login(request, user)
            #messages.success(request, "Hospital login successful.")
            #return redirect('accounts:hospital_dashboard')
        #else:
            #messages.error(request, "Invalid credentials.")
    #return render(request, 'accounts/hospital_login.html')

def hospital_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                hospital = Hospital.objects.get(user=user)
                if hospital.approved:   # check if approved by admin
                    login(request, user)
                    messages.success(request, "Login successful.")
                    return redirect("accounts:hospital_dashboard")
                else:
                    messages.error(request, "Your hospital is not yet approved by admin.")
            except Hospital.DoesNotExist:
                messages.error(request, "No hospital profile found.")
        else:
            messages.error(request, "Invalid credentials.")

    return render(request, "accounts/hospital_login.html")

# In accounts/views.py (Corrected hospital_dashboard)

@login_required
def hospital_dashboard(request):
    # Only proceed if the user is a hospital and is approved
    try:
        # Tries to get the linked Hospital object
        hospital = Hospital.objects.get(user=request.user)
    except Hospital.DoesNotExist:
        # If the user is logged in but doesn't have a hospital profile (e.g., they are a Parent)
        messages.error(request, "Access denied. You must log in as an approved Hospital.")
        return redirect('accounts:hospital_login')

    if not hospital.approved: # Ensure consistency with 'is_approved' field
        messages.error(request, "Your hospital is registered but not yet approved by the administrator.")
        # Log the user out since they shouldn't be here
        logout(request) 
        return redirect('accounts:hospital_login')

    # hospital object is guaranteed to be linked and approved here
    return render(request, 'accounts/hospital_dashboard.html', {'hospital': hospital})

def is_superuser(user):
    """Helper function to check for Siperuser status"""
    return user.is_superuser

# Admin views for approval
@login_required
@user_passes_test(is_superuser)
def approve_hospitals(request):
    pending = Hospital.objects.filter(approved=False)
    return render(request, 'accounts/approve_hospitals.html', {'hospitals': pending})

@login_required
@user_passes_test(is_superuser)
def approve_hospital(request, hospital_id):
    hospital = get_object_or_404(Hospital, id=hospital_id)
    if request.method=='POST':
        hospital.approved = True
        hospital.save()

        if not hospital.user.is_active:
            hospital.user.is_active=True
            hospital.user.save()
        messages.success(request, f"Hospital '{hospital.name}' approved.")
    return redirect('accounts:approve_hospitals')

@login_required
@user_passes_test(is_superuser)
def reject_hospital(request, hospital_id):
    hospital = get_object_or_404(Hospital, id=hospital_id)
    if request.method=='POST':
    # you can delete or mark rejected. Here we delete:
        hospital.user.delete()   # deletes linked user
    #hospital.delete()
        messages.success(request, "Hospital rejected and removed.")
    return redirect('accounts:approve_hospitals')

@login_required
def book_appointment(request):
    parent = Parent.objects.filter(user=request.user).first()
    if not parent:
        messages.error(request, "No parent profile found. Please register first.")
        return redirect('accounts:parent_register')
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.parent = parent
            appointment.save()
            messages.success(request, "Appointment booked successfully!")
            return redirect('accounts:view_appointments')
    else:
        form = AppointmentForm()
    return render(request, 'accounts/book_appointment.html', {'form': form})


@login_required
def view_appointments(request):
    parent = Parent.objects.filter(user=request.user).first()
    appointments = Appointment.objects.filter(parent=parent).order_by('date')
    return render(request, 'accounts/view_appointments.html', {'appointments': appointments})
