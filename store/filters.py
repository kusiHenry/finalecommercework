import django_filters
from .models import *



class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        ordering = ['name']
        fields = {'name':['icontains'], 'brand':['icontains'], 'category':['icontains'],}
        
        