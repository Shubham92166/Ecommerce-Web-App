from admin_honeypot import views
from django.urls import path

app_name = 'admin_honeypot'

urlpatterns = [
    path('login/', views.AdminHoneypot.as_view(), name='login'),
    path('', views.AdminHoneypot.as_view(), name='index'),
]
