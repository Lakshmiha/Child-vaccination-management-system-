from django.contrib import admin
from .models import Parent, Child, Hospital, Vaccine, Appointment


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'address']
    search_fields = ['user__username', 'phone_number']


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'date_of_birth', 'gender', 'blood_group']
    list_filter = ['gender']
    search_fields = ['name', 'parent__user__username']


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'approved']
    list_filter = ['approved']
    search_fields = ['name', 'email']
    actions = ['approve_hospitals']

    def approve_hospitals(self, request, queryset):
        queryset.update(approved=True)
        for hospital in queryset:
            if hospital.user:
                hospital.user.is_active = True
                hospital.user.save()
    approve_hospitals.short_description = "Approve selected hospitals"


@admin.register(Vaccine)
class VaccineAdmin(admin.ModelAdmin):
    list_display = ['name', 'recommended_age', 'description']
    search_fields = ['name']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['child', 'hospital', 'parent', 'date', 'time', 'status', 'created_at']
    list_filter = ['status', 'date', 'hospital']
    search_fields = ['child__name', 'parent__user__username', 'hospital__name']
    date_hierarchy = 'date'