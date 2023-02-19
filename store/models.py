from django.db import models
from category.models import Category
from django.urls import reverse
from account.models import Account

class Product(models.Model):
    product_name = models.CharField(max_length=100, unique= True)
    slug = models.SlugField(max_length=100)
    description = models.TextField(max_length=500, blank=True)
    price = models.IntegerField()
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='photos/product')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True)


    def get_url(self):
        return reverse('product_detail', args = [self.category.slug, self.slug])

    def __str__(self):
        return self.product_name

variation_category_choices = {
    ('colour', 'colour'),
    ('size', 'size'),
}

class VariationManager(models.Manager):
    def colours(self):
        return super(VariationManager, self).filter(variation_category = 'colour', is_active = True)
    
    def sizes(self):
        return super(VariationManager, self).filter(variation_category = 'size', is_active = True)


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category_choices, default='Green')
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_by = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.variation_value

    object = VariationManager()

class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50, blank=True)
    review = models.TextField(max_length=500, blank= True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject




