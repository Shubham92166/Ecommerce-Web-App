from django.shortcuts import render, get_object_or_404
from .models import Product
from category.models import Category

def store(request, category_slug = None):
    categories = None
    allAvailableProducts = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug = category_slug)
        allAvailableProducts = Product.objects.filter(category = categories, is_available = True)
        productCount = allAvailableProducts.count()
    else:
        allAvailableProducts = Product.objects.all().filter(is_available = True)
        productCount = allAvailableProducts.count()
    context = {
        'allAvailableProducts' : allAvailableProducts, 
        'productCount': productCount, 
    }
    return render(request, 'store/store.html', context)