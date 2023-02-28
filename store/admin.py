from django.contrib import admin
from .models import Product, Variation

# Register your models here.


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'formatted_price', 'formatted_cost',
                    'stock', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}

    def formatted_price(self, obj):
        return '$' + str(obj.price)
    formatted_price.short_description = 'Price'

    def formatted_cost(self, obj):
        return '$' + str(obj.cost)
    formatted_cost.short_description = 'Cost'


class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category',
                    'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category',
                   'variation_value')


admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
