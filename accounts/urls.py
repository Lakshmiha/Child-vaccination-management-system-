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
]