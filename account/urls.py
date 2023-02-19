#Django import
from django.urls import path 

#local import
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

    path('my-orders/', views.my_orders, name = "my-orders"),
    path('edit-profile/', views.edit_profile, name='edit-profile'),
    path('change-password/', views.change_password, name = 'change-password'),
    path('order-detail/<int:order_id>/', views.order_detail, name='order-detail'),
    path('change-password/', views.change_password, name='change-password'),
]