from django.shortcuts import render, redirect
from .form import OrderForm
from .models import Order
from cart.models import CartItem
import datetime
from django.contrib.auth.decorators import login_required

@login_required(login_url = 'login')
def place_order(request):
    current_user = request.user

    grand_total = 0
    tax = 0
    total = 0
    quantity = 0

    cart_items = CartItem.objects.filter(user = current_user)

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    
    tax_amount = (5*total)/100

    grand_total = tax_amount + total

    if request.method == 'POST':
        form = OrderForm(request.POST)
         
        if form.is_valid():
        
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.email = form.cleaned_data['email']
            data.phone_number = form.cleaned_data['phone_number']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.city = form.cleaned_data['city']
            data.state = form.cleaned_data['state']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.ip = request.META.get('REMOTE_ADDR')
            data.tax = tax
            data.save()

            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))

            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user = current_user, is_ordered = False, order_number = order_number)
            context = {
                'order' : order,
                'cart_items' : cart_items,
                'total' : total,
                'tax_amount' : tax_amount, 
                'grand_total' : grand_total,
            }
            return render(request, 'order/payment.html', context)
        
    else:
        return redirect('checkout')

@login_required(login_url = 'login')
def payment(request):
    return render(request, "order/payment.html")

