#Django import
from django.urls import path

#local import
from . import views

urlpatterns = [
    path('place-order/', views.place_order, name="place-order"),
    path('payment/', views.payment, name="payment"),
    path('order-complete/', views.order_complete, name="order-complete")
]