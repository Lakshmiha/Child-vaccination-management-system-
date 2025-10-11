from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from datetime import date
from django.http import JsonResponse
from .forms import ParentRegistrationForm, ChildForm, HospitalRegisterForm, AppointmentForm
from .models import Parent, Child, Hospital, Appointment, Vaccine,Inventory


def home(request):  
    """Root URL: redirect to dashboard if logged in, else to login"""
    if request.user.is_authenticated:
        if Parent.objects.filter(user=request.user).exists():
            return redirect('accounts:parent_dashboard')
        elif Hospital.objects.filter(user=request.user).exists():
            return redirect('accounts:hospital_dashboard')
    return render(request, 'accounts/home.html')


# ==================== PARENT VIEWS ====================

def parent_register(request):
    if request.method == "POST":
        form = ParentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. Please log in.")
            return redirect("accounts:parent_login")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ParentRegistrationForm()
    return render(request, "accounts/parent_register.html", {"form": form})


def parent_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if Parent.objects.filter(user=user).exists():
                login(request, user)
                messages.success(request, "Login successful.")
                return redirect('accounts:parent_dashboard')
            else:
                messages.error(request, "This account is not registered as a Parent.")
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, "accounts/parent_login.html")


def parent_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('accounts:parent_login')


@login_required
def parent_dashboard(request):
    try:
        parent = Parent.objects.get(user=request.user)
    except Parent.DoesNotExist:
        messages.error(request, "No parent profile found.")
        return redirect('accounts:home')

    children = Child.objects.filter(parent=parent)

    # Use date/time for ordering to match the rest of your codebase
    recent_appointments = Appointment.objects.filter(parent=parent).order_by('-date', '-time')[:5]

    # Aggregate counts
    total_appointments_count = Appointment.objects.filter(parent=parent).count()
    completed_appointments_count = Appointment.objects.filter(
        parent=parent, status='Completed'
    ).count()

    # If you want "completed among recent 5"
    completed_recent_count = sum(1 for a in recent_appointments if a.status == "Completed")

    return render(request, "accounts/parent_dashboard.html", {
        "parent": parent,
        "children": children,
        "recent_appointments": recent_appointments,
        "total_appointments_count": total_appointments_count,
        "completed_appointments_count": completed_appointments_count,
        "completed_recent_count": completed_recent_count,
    })


@login_required
def add_child(request):
    parent = Parent.objects.filter(user=request.user).first()
    
    if not parent:
        messages.error(request, "No parent profile found.")
        return redirect('accounts:parent_dashboard')
    
    if request.method == "POST":
        form = ChildForm(request.POST)
        if form.is_valid():
            child = form.save(commit=False)
            child.parent = parent
            child.save()
            messages.success(request, f"Child '{child.name}' added successfully.")
            return redirect('accounts:parent_dashboard')
    else:
        form = ChildForm()
    
    return render(request, "accounts/add_child.html", {"form": form})


@login_required
def view_children(request):
    parent = Parent.objects.filter(user=request.user).first()
    
    if not parent:
        messages.error(request, "No parent profile found.")
        return redirect('accounts:parent_dashboard')
    
    children = Child.objects.filter(parent=parent)
    return render(request, "accounts/view_children.html", {"children": children})


@login_required
def edit_child(request, child_id):
    child = get_object_or_404(Child, id=child_id, parent__user=request.user)
    
    if request.method == "POST":
        form = ChildForm(request.POST, instance=child)
        if form.is_valid():
            form.save()
            messages.success(request, f"Child '{child.name}' updated successfully.")
            return redirect('accounts:view_children')
    else:
        form = ChildForm(instance=child)
    
    return render(request, "accounts/edit_child.html", {"form": form, "child": child})


@login_required
def delete_child(request, child_id):
    child = get_object_or_404(Child, id=child_id, parent__user=request.user)
    
    if request.method == "POST":
        child_name = child.name
        child.delete()
        messages.success(request, f"Child '{child_name}' deleted successfully.")
        return redirect('accounts:view_children')
    
    return render(request, "accounts/delete_child.html", {"child": child})


# ==================== HOSPITAL VIEWS ====================

def hospital_register(request):
    if request.method == "POST":
        form = HospitalRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Hospital registered successfully! Awaiting admin approval.")
            return redirect('accounts:hospital_login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = HospitalRegisterForm()
    
    return render(request, 'accounts/hospital_register.html', {'form': form})


def hospital_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                hospital = Hospital.objects.get(user=user)
                if hospital.approved:
                    login(request, user)
                    messages.success(request, f"Welcome, {hospital.name}!")
                    return redirect("accounts:hospital_dashboard")
                else:
                    messages.warning(request, "Your hospital registration is pending admin approval.")
            except Hospital.DoesNotExist:
                messages.error(request, "No hospital profile found for this account.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "accounts/hospital_login.html")


def hospital_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('accounts:hospital_login')


@login_required
def hospital_dashboard(request):
    try:
        hospital = Hospital.objects.get(user=request.user)
    except Hospital.DoesNotExist:
        messages.error(request, "Access denied. You must log in as an approved hospital.")
        return redirect('accounts:hospital_login')

    if not hospital.approved:
        messages.error(request, "Your hospital is registered but not yet approved by the administrator.")
        logout(request)
        return redirect('accounts:hospital_login')

    # Get appointment statistics
    total_appointments = Appointment.objects.filter(hospital=hospital).count()
    pending_count = Appointment.objects.filter(hospital=hospital, status='Pending').count()
    approved_count = Appointment.objects.filter(hospital=hospital, status='Approved').count()
    completed_count = Appointment.objects.filter(hospital=hospital, status='Completed').count()

    context = {
        'hospital': hospital,
        'total_appointments': total_appointments,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'completed_count': completed_count,
    }
    
    return render(request, 'accounts/hospital_dashboard.html', context)


@login_required
def hospital_appointments(request):
    try:
        hospital = Hospital.objects.get(user=request.user)
    except Hospital.DoesNotExist:
        messages.error(request, "Access denied. Please log in as a hospital.")
        return redirect("accounts:hospital_login")

    # Get all appointments for this hospital
    appointments = Appointment.objects.filter(hospital=hospital).select_related(
        'child', 'parent', 'parent__user', 'vaccine'
    ).order_by('date', 'time')
    
    # Filter by status - match template variable names
    pending_appointments = appointments.filter(status="Pending")
    confirmed_appointments = appointments.filter(status="Approved")  # Template uses 'confirmed_appointments'
    completed_appointments = appointments.filter(status="Completed")
    cancelled_appointments = appointments.filter(status="Cancelled")
    
    context = {
        "hospital": hospital,
        "all_appointments": appointments,
        "pending_appointments": pending_appointments,
        "confirmed_appointments": confirmed_appointments,
        "completed_appointments": completed_appointments,
        "cancelled_appointments": cancelled_appointments,
    }
    
    return render(request, "accounts/hospital_appointments.html", context)


@login_required
def update_appointment_status(request, appointment_id):
    try:
        hospital = Hospital.objects.get(user=request.user)
    except Hospital.DoesNotExist:
        messages.error(request, "Access denied.")
        return redirect("accounts:hospital_login")

    appointment = get_object_or_404(Appointment, id=appointment_id, hospital=hospital)

    if request.method == "POST":
        new_status = request.POST.get("status")
        
        valid_statuses = ['Pending', 'Approved', 'Completed', 'Cancelled']
        
        if new_status in valid_statuses:
            appointment.status = new_status
            appointment.save()
            messages.success(request, f"Appointment for {appointment.child.name} updated to '{new_status}'.")
        else:
            messages.error(request, "Invalid status value.")
        
        return redirect("accounts:hospital_appointments")

    return render(request, "accounts/update_appointment_status.html", {
        "appointment": appointment,
        "status_choices": Appointment.STATUS_CHOICES
    })


@login_required
def hospital_confirm_appointment(request, appointment_id):
    """Quick approve action for hospitals"""
    try:
        hospital = Hospital.objects.get(user=request.user)
    except Hospital.DoesNotExist:
        messages.error(request, "Access denied.")
        return redirect("accounts:hospital_login")

    appointment = get_object_or_404(Appointment, id=appointment_id, hospital=hospital)

    
    if not appointment.vaccine:
        messages.error(request, "Cannot approve appointment: No vaccine selected.")
        return redirect("accounts:hospital_appointments")

    

    inventory_item = Inventory.objects.filter(hospital=hospital, vaccine=appointment.vaccine).first()

    # ✅ If not available or zero stock → reject approval
    if not inventory_item or inventory_item.stock_quantity <= 0:
        messages.error(request, f"Cannot approve. '{appointment.vaccine.name}' is OUT OF STOCK.")
        return redirect("accounts:hospital_appointments")

    # ✅ If stock available → approve & reduce stock
    if request.method == "POST":
        appointment.status = "Approved"
        appointment.save()

        inventory_item.stock_quantity -= 1
        inventory_item.save()

        messages.success(request, f"Appointment approved and 1 dose of '{appointment.vaccine.name}' deducted from stock.")

    return redirect("accounts:hospital_appointments")

# ==================== APPOINTMENT VIEWS (PARENT) ====================

@login_required
def book_appointment(request):
    parent = Parent.objects.filter(user=request.user).first()
    
    if not parent:
        messages.error(request, "No parent profile found. Please complete your registration.")
        return redirect('accounts:parent_register')
    
    if not Child.objects.filter(parent=parent).exists():
        messages.warning(request, "Please add at least one child before booking an appointment.")
        return redirect('accounts:add_child')
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, parent=parent)
        
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.parent = parent
            appointment.status = "Pending"
            appointment.save()
            
            messages.success(
                request, 
                f"Appointment booked for {appointment.child.name} "
                f"at {appointment.hospital.name} on {appointment.date} at {appointment.time}."
            )
            return redirect('accounts:view_appointments')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = AppointmentForm(parent=parent)
    
    return render(request, 'accounts/book_appointment.html', {'form': form})


@login_required
def view_appointments(request):
    parent = Parent.objects.filter(user=request.user).first()
    
    if not parent:
        messages.error(request, "No parent profile found.")
        return redirect('accounts:parent_dashboard')
    
    appointments = Appointment.objects.filter(parent=parent).select_related(
        'child', 'hospital', 'vaccine'
    ).order_by('-date', '-time')
    
    # Separate upcoming and past appointments
    today = date.today()
    upcoming = appointments.filter(date__gte=today).exclude(status='Cancelled')
    past = appointments.filter(Q(date__lt=today) | Q(status='Cancelled'))
    
    context = {
        'appointments': appointments,
        'upcoming_appointments': upcoming,
        'past_appointments': past,
    }
    
    return render(request, 'accounts/view_appointments.html', context)


@login_required
def cancel_appointment(request, appointment_id):
    """Allow parent to cancel their appointment"""
    parent = Parent.objects.filter(user=request.user).first()
    appointment = get_object_or_404(Appointment, id=appointment_id, parent=parent)
    
    if request.method == "POST":
        if appointment.status in ['Pending', 'Approved']:
            appointment.status = 'Cancelled'
            appointment.save()
            messages.success(request, "Appointment cancelled successfully.")
        else:
            messages.error(request, "This appointment cannot be cancelled.")
        return redirect('accounts:view_appointments')
    
    return render(request, 'accounts/cancel_appointment.html', {'appointment': appointment})


# ==================== ADMIN VIEWS ====================

def is_superuser(user):
    """Helper function to check for superuser status"""
    return user.is_superuser


@login_required
@user_passes_test(is_superuser)
def approve_hospitals(request):
    pending = Hospital.objects.filter(approved=False).order_by('id')
    approved = Hospital.objects.filter(approved=True).order_by('name')
    
    context = {
        'pending_hospitals': pending,
        'approved_hospitals': approved,
    }
    
    return render(request, 'accounts/approve_hospitals.html', context)


@login_required
@user_passes_test(is_superuser)
def approve_hospital(request, hospital_id):
    hospital = get_object_or_404(Hospital, id=hospital_id)
    
    if request.method == 'POST':
        hospital.approved = True
        hospital.save()

        if not hospital.user.is_active:
            hospital.user.is_active = True
            hospital.user.save()
        
        messages.success(request, f"Hospital '{hospital.name}' has been approved.")
    
    return redirect('accounts:approve_hospitals')


@login_required
@user_passes_test(is_superuser)
def reject_hospital(request, hospital_id):
    hospital = get_object_or_404(Hospital, id=hospital_id)
    
    if request.method == 'POST':
        hospital_name = hospital.name
        user = hospital.user
        
        hospital.delete()
        
        messages.success(request, f"Hospital '{hospital_name}' has been rejected and removed.")
    
    return redirect('accounts:approve_hospitals')

# --- In accounts/views.py ---

# ... imports ...
# ... existing views ...

# ==================== HOSPITAL INVENTORY VIEWS ====================

@login_required
def hospital_inventory(request):
    try:
        hospital = Hospital.objects.get(user=request.user)
    except Hospital.DoesNotExist:
        messages.error(request, "Access denied. Please log in as a hospital.")
        return redirect("accounts:hospital_login")

    # Fetch all inventory items for this hospital
    inventory_items = Inventory.objects.filter(hospital=hospital).select_related('vaccine').order_by('vaccine__name')
    
    # Identify vaccines not currently in the inventory for an "Add New" feature
    existing_vaccine_ids = inventory_items.values_list('vaccine_id', flat=True)
    available_vaccines_to_add = Vaccine.objects.exclude(id__in=existing_vaccine_ids)

    context = {
        'hospital': hospital,
        'inventory_items': inventory_items,
        'available_vaccines_to_add': available_vaccines_to_add,
    }
    return render(request, 'accounts/hospital_inventory.html', context)


@login_required
def update_inventory_stock(request, inventory_id=None, vaccine_id=None):
    try:
        hospital = Hospital.objects.get(user=request.user)
    except Hospital.DoesNotExist:
        messages.error(request, "Access denied.")
        return redirect("accounts:hospital_login")

    if inventory_id:
        inventory = get_object_or_404(Inventory, id=inventory_id, hospital=hospital)
        vaccine_name = inventory.vaccine.name
    elif vaccine_id:
        vaccine = get_object_or_404(Vaccine, id=vaccine_id)
        # Check if inventory already exists (shouldn't happen if view is used correctly)
        inventory, created = Inventory.objects.get_or_create(
            hospital=hospital, 
            vaccine=vaccine, 
            defaults={'stock_quantity': 0}
        )
        vaccine_name = vaccine.name
    else:
        messages.error(request, "Invalid request.")
        return redirect('accounts:hospital_inventory')

    if request.method == 'POST':
        new_stock = request.POST.get('stock_quantity')
        try:
            new_stock = int(new_stock)
            if new_stock < 0:
                raise ValueError("Stock cannot be negative.")
                
            inventory.stock_quantity = new_stock
            inventory.save()
            messages.success(request, f"Stock for {vaccine_name} updated to {new_stock}.")
        except ValueError:
            messages.error(request, "Invalid stock quantity entered.")
        
        return redirect('accounts:hospital_inventory')

    context = {
        'inventory': inventory,
        'vaccine_name': vaccine_name,
    }
    return render(request, 'accounts/update_inventory_stock.html', context)

# --- In accounts/views.py ---


# ... other imports ...

def get_available_vaccines_api(request, hospital_id):
    """API endpoint for AJAX to fetch available vaccines for a given hospital."""
    try:
        hospital = Hospital.objects.get(id=hospital_id)
        
        # Filter Inventory where stock > 0 for the hospital
        available_inventory = Inventory.objects.filter(
            hospital=hospital, 
            stock_quantity__gt=0
        ).select_related('vaccine')
        
        vaccine_list = [
            {'id': item.vaccine.id, 'name': item.vaccine.name}
            for item in available_inventory
        ]
        
        return JsonResponse({'vaccines': vaccine_list})
        
    except Hospital.DoesNotExist:
        return JsonResponse({'error': 'Hospital not found'}, status=404)