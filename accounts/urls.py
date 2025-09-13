from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.parent_register, name='parent_register'),
    path('login/', views.parent_login, name='parent_login'),
    path('logout/', views.parent_logout, name='parent_logout'),
    path('dashboard/', views.parent_dashboard, name='parent_dashboard'),
]
