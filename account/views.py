from django.shortcuts import render, redirect, get_object_or_404
from .form import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from cart.views import _cart_id
from cart.models import Cart, CartItem
import requests
from order.models import Order, OrderProduct

def _get_current_site(request):
    return get_current_site(request)

#verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes

def _send_mail(current_site, email_subject, template_to_render, user, to, data = None):
    
    message = render_to_string(template_to_render, {
        'user' : user, 
        'domain' : current_site, 
        'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
        'token' : default_token_generator.make_token(user),
        'data' : data,
    })

    to_mail = to
    send_mail = EmailMessage(email_subject, message, to= [to_mail])
    send_mail.content_subtype = "html"
    send_mail.send()


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            username = email.split('@')[0]
            phone_number = form.cleaned_data['phone_number']
            user = Account.objects.create_user(first_name = first_name, last_name = last_name, email = email, username = username, password = password)
            user.phone_number = phone_number
            user.save()

            #Create uer profile
            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = 'default/default.png'
            profile.save()

            #USER ACTIVATION
            current_site = _get_current_site(request)
            email_subject = 'Action Required-Please activate your account'
            template = "account/account_activation_mail.html"
            _send_mail(current_site, email_subject, template, user, email)
            
            messages.success(request, "Registration successful")
            return redirect('register')

    else:
        form = RegistrationForm()
    context = {
        'form' : form,
    }
    return render(request, 'account/register.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email = email, password = password)

        if user:
            try:
                cart = Cart.objects.get(cart_id = _cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart = cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart = cart)

                    #Getting the product variations by cart id
                    product_variation = []

                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    #get the cart item from the user to access his product variations
                    cart_item = CartItem.objects.filter(user = user)
                    existing_variation_list = []
                    id = []
                    for item in cart_item:
                        existing_variations = item.variations.all()
                        existing_variation_list.append(list(existing_variations))
                        id.append(item.id)
                    
                    for product in product_variation:
                        if product in existing_variation_list:
                            index = existing_variation_list.index(product)
                            item_id = id[index]
                            item = CartItem.objects.get(id = item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart= cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            
            except:
                pass

            auth.login(request, user)
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    next_page = params['next']
                    return redirect(next_page)
            except:
                return redirect('home')

        else:
            messages.error(request, 'Invalid credentials. Please try again!')
            return redirect('login')

    return render(request, 'account/login.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('login')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk = uid)
    except (TypeError, ValueError, Account.DoesNotExist):
        user = None
    
    if user:
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated successfully')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')


@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id = request.user.id, is_ordered = True)
    orders_count = orders.count()
    user_profile = get_object_or_404(UserProfile, user = request.user)

    context = {
        'orders_count' : orders_count,
        'user_profile' : user_profile
    }
    return render(request, 'account/dashboard.html', context)


def forgot_password(request):
    if request.method == 'POST':
        user_email = request.POST['email']
        if Account.objects.filter(email = user_email).exists():
            user = Account.objects.get(email__iexact = user_email)
            current_site = _get_current_site(request)
            email_subject = "Action Required-Reset password"
            template = "account/reset_password_mail.html"

            _send_mail(current_site, email_subject, template, user, user_email)
            messages.success(request, 'Password reset email has been sent to your registered email')
            return redirect('login')

        else:
            messages.error(request, "Sorry, this account doesn't exist!")

    return render(request, 'account/forgot_password.html')


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk = uid)

    except (TypeError, ValueError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, "Please reset your password")
        return redirect("reset_password")
    else:
        messages.error(request, "This link has expired")
        return redirect('login')
    

def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk = uid)
            user.set_password(password)
            messages.success(request, 'Password is changed successfully')
            return redirect('login')
        else:
            messages.error(request, "Password do not match!")
            return redirect('reset_password')
    return render(request, 'account/reset_password.html')


@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user = request.user, is_ordered = True).order_by('-created_at')
    context = {
        'orders' : orders,
    }
    return render(request, 'account/my_orders.html', context)


@login_required(login_url='login')
def change_password(request):
    return render(request, 'account/change-password.html')
 
def order_detail(request, order_id):
    
    try:
        order = Order.objects.get(order_number = order_id, is_ordered = True)
        ordered_products = OrderProduct.objects.filter(order__order_number = order_id)

        total = order.order_total
        tax_amount = order.tax
        sub_total = total - tax_amount


        context = {
            'order' : order,
            'ordered_products' : ordered_products,
            'order_number' : order.order_number,
            'sub_total' : sub_total,
        }
        return render(request, 'account/order-detail.html', context)
    except:
        pass
    return render(request, 'account/order-detail.html')

@login_required(login_url="login")
def edit_profile(request):
    user_profile = get_object_or_404(UserProfile, user = request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully")
            return redirect('edit-profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)
    
    context = {
        'user_form' : user_form,
        'profile_form' : profile_form,
        'user_profile' : user_profile
    }

    return render(request, 'account/edit-profile.html', context)

@login_required(login_url="login")
def change_password(request):
    if request.method == "POST":
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact = request.user.username)
        if new_password == confirm_password:
            is_current_password_validated = user.check_password(current_password)
            if is_current_password_validated:
                user.set_password(new_password)
                user.save()
                return redirect('change-password')
            else:
                messages.error(request, "Invalid existing password")
                return redirect('change-password')
        else:
            messages.error(request, 'New password and confirm password do not match!')
            return redirect('change-password')
    return render(request, 'account/change-password.html')


