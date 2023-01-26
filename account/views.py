from django.shortcuts import render, redirect
from .form import RegistrationForm
from .models import Account
from django.contrib import messages

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
            messages.success(request, "Registration successful")
            return redirect('register')

    else:
        form = RegistrationForm()
    context = {
        'form' : form,
    }
    return render(request, 'account/register.html', context)

def login(request):
    return render(request, 'account/login.html')

def logout(request):
    return 
