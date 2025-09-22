from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.parent_register, name='parent_register'),
    path('login/', views.parent_login, name='parent_login'),
    path('logout/', views.parent_logout, name='parent_logout'),
    path('dashboard/', views.parent_dashboard, name='parent_dashboard'),
    path('add-child/', views.add_child, name='add_child'),
    path('children/', views.view_children, name='view_children'),
    path('edit-child/<int:child_id>/', views.edit_child, name='edit_child'),
    path('delete-child/<int:child_id>/', views.delete_child, name='delete_child'),
]
