from django.shortcuts import render, redirect
from .form import OrderForm
from .models import Order, Payment, OrderProduct
from cart.models import CartItem
import datetime
from django.contrib.auth.decorators import login_required
import json
from store.models import Product
from account.views import _send_mail, _get_current_site

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
    body = json.loads(request.body)
    order = Order.objects.get(user = request.user, is_ordered = False, order_number = body['orderId'])
    payment = Payment(
        user = request.user, 
        payment_id = body['transactionId'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )

    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()

    #Move the cart items to Order product table
    cart_items = CartItem.objects.filter(user = request.user)

    for item in cart_items:
        order_product = OrderProduct()
        order_product.order_id = order.id 
        order_product.payment = payment
        order_product.user_id = request.user.id 
        order_product.product_id = item.product_id
        order_product.quantity = item.quantity
        order_product.product_price = item.product.price
        order_product.is_ordered = True
        order_product.save()
        
        cart_item = CartItem.objects.get(id = item.id)
        product_variations = cart_item.variations.all()
        order_product.variations.set(product_variations)
        order_product.save()

        #Reduce the quantity of the sold products
        product = Product.objects.get(id = item.product_id)
        product.stock -= item.quantity
        product.save()

    #Clear the cart after placing the order
    CartItem.objects.filter(user = request.user).delete()

    #Send order complettion email
    current_site = _get_current_site(request)
    email_subject = "Thank you for your order!"
    template = "order/order_received_email.html"
    user = request.user
    user_email = user.email
    data = order
    _send_mail(current_site, email_subject, template, user, user_email, data)

    return render(request, "order/payment.html")

