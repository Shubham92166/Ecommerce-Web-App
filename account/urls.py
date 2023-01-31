from django.urls import path 
from . import views

urlpatterns = [
    path('register/', views.register, name = 'register'),
    path('login/', views.login, name = 'login'),
    path('logout/', views.logout, name = 'logout'),
    path('active/<uidb64>/<token>/', views.activate, name = 'activate'),
    path('dashboard/', views.dashboard, name = 'dashboard'),
    path('forgot-password/', views.forgot_password, name = 'forgot_password'),
    path('reset-password-validate/<uidb64>/<token>/', views.reset_password_validate, name = 'reset_password_validate'),
    path('reset_password/', views.reset_password, name = "reset_password"),
]