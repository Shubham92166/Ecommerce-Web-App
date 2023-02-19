#Django imports 
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages

#local imports
from .models import Product, ReviewRating
from category.models import Category
from cart.models import CartItem
from cart.views import _cart_id
from order.models import OrderProduct
from .forms import ReviewForm

def store(request, category_slug = None):
    categories = None
    all_available_products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug = category_slug)
        all_available_products = Product.objects.filter(category = categories, is_available = True).order_by('id')
        paginator = Paginator(all_available_products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = all_available_products.count()
    else:
        all_available_products = Product.objects.all().filter(is_available = True).order_by('id')
        paginator = Paginator(all_available_products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = all_available_products.count()

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
    
    if request.user.is_authenticated:
        try:
            product_purchased_before = OrderProduct.objects.filter(user = request.user, product__id = single_product.id).exists()
        except OrderProduct.DoesNotExist:
            product_purchased_before = False
    else:
        product_purchased_before = False
    
    #Get all reviews for the given product id
    all_reviews = ReviewRating.objects.filter(product__id = single_product.id, is_active = True)

    context = {
        'single_product' : single_product, 
        'in_cart' : in_cart,
        'product_purchased_before' : product_purchased_before,
        'all_reviews' : all_reviews,
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

def add_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            user_review = ReviewRating.objects.get(user__id = request.user.id, product__id = product_id)
            review_form = ReviewForm(request.POST, instance=user_review)
            review_form.save()
            messages.success(request, "Thank you! Your review has been updated successfully")
            return redirect(url)

        except ReviewRating.DoesNotExist:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                data = ReviewRating()
                data.subject = review_form.cleaned_data['subject']
                data.rating = review_form.cleaned_data['rating']
                data.review = review_form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, "Your review has been added successfully")
                return redirect(url)
