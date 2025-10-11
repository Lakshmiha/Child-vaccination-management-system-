from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Parent URLs
    path('register/', views.parent_register, name='parent_register'),
    path('login/', views.parent_login, name='parent_login'),
    path('logout/', views.parent_logout, name='parent_logout'),
    path('dashboard/', views.parent_dashboard, name='parent_dashboard'),
    
    # Child Management
    path('add-child/', views.add_child, name='add_child'),
    path('children/', views.view_children, name='view_children'),
    path('edit-child/<int:child_id>/', views.edit_child, name='edit_child'),
    path('delete-child/<int:child_id>/', views.delete_child, name='delete_child'),
    
    # Hospital URLs
    path('hospital/register/', views.hospital_register, name='hospital_register'),
    path('hospital/login/', views.hospital_login, name='hospital_login'),
    path('hospital/logout/', views.hospital_logout, name='hospital_logout'),
    path('hospital/dashboard/', views.hospital_dashboard, name='hospital_dashboard'),
    path('hospital/appointments/', views.hospital_appointments, name='hospital_appointments'),
    path('hospital/appointment/update/<int:appointment_id>/', views.update_appointment_status, name='update_appointment_status'),
    path('hospital/appointment/confirm/<int:appointment_id>/', views.hospital_confirm_appointment, name='hospital_confirm_appointment'),
    
    # Admin URLs
    path('hospitals/pending/', views.approve_hospitals, name='approve_hospitals'),
    path('hospitals/approve/<int:hospital_id>/', views.approve_hospital, name='approve_hospital'),
    path('hospitals/reject/<int:hospital_id>/', views.reject_hospital, name='reject_hospital'),
    
    # Appointment URLs (Parent)
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    path('view-appointments/', views.view_appointments, name='view_appointments'),
    path('appointment/cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    # --- In accounts/urls.py ---

# ... existing Parent and Hospital URLs ...

# Hospital Inventory Management
    path('hospital/inventory/', views.hospital_inventory, name='hospital_inventory'),
    path('hospital/inventory/update/<int:inventory_id>/', views.update_inventory_stock, name='update_inventory_stock'),
    path('hospital/inventory/add/<int:vaccine_id>/', views.update_inventory_stock, name='add_inventory_stock'),
    # --- In accounts/urls.py ---

# ... existing URLs ...

# API endpoint for AJAX
    path('api/get-available-vaccines/<int:hospital_id>/', views.get_available_vaccines_api, name='get_available_vaccines_api'),

# ... other URLs ...
# ... other URLs ...
]