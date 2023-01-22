from django.shortcuts import render, get_object_or_404
from .models import Product
from category.models import Category
from cart.models import CartItem
from cart.views import _cart_id
from django.core.paginator import Paginator
from django.db.models import Q
def store(request, category_slug = None):
    categories = None
    allAvailableProducts = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug = category_slug)
        allAvailableProducts = Product.objects.filter(category = categories, is_available = True)
        paginator = Paginator(allAvailableProducts, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = allAvailableProducts.count()
    else:
        allAvailableProducts = Product.objects.all().filter(is_available = True).order_by(id)
        paginator = Paginator(allAvailableProducts, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = allAvailableProducts.count()

    context = {
        'paged_products' : paged_products, 
        'product_count': product_count, 
    }

    return render(request, 'store/store.html', context)


def product_detail(request, category_slug = None, product_slug = None):
    try:
        single_product = Product.objects.get(category__slug = category_slug, slug = product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request), product = single_product).exists()
    except Exception as e:
        raise e
    
    context = {
        'single_product' : single_product, 
        'in_cart' : in_cart,
    }
    return render(request, 'store/product_detail.html', context)

def search(request):
    if "keyword" in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            paged_products = Product.objects.order_by('-created_date').filter(Q(product_name__icontains = keyword) | Q(description__icontains = keyword)).filter(is_available = True)
            product_count = paged_products.count()

    context = {
        'paged_products' : paged_products,
        'product_count' : product_count,
    }

    return render(request, 'store/store.html', context)

    
