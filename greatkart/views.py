from django.shortcuts import render
from store.models import Product

def home(request):
    allAvailableProducts = Product.objects.all().filter(is_available = True)
    context = {
        'allAvailableProducts' : allAvailableProducts,
    }
    return render(request, 'home.html', context)
    
