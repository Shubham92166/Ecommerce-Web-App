#Django imports
from django.shortcuts import render

#local imports
from store.models import Product

def home(request):
    all__available_products = Product.objects.all().filter(is_available = True)
    context = {
        'all__available_products' : all__available_products,
    }
    return render(request, 'home.html', context)
    
