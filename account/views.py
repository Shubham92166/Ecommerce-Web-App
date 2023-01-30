from django.shortcuts import render, redirect
from .form import RegistrationForm
from .models import Account
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.decorators import login_required

#verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes

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


            #USER ACTIVATION

            current_site = get_current_site(request)
            mail_subject = 'Action Required-Please activate your account'
            message = render_to_string('account/account_activation_mail.html', {
                'user' : user, 
                'domain' : current_site, 
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
            })

            to_mail = email
            send_mail = EmailMessage(mail_subject, message, to= [to_mail])
            send_mail.send()
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
            auth.login(request, user)
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
    return render(request, 'account/dashboard.html')
