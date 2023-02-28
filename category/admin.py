from django.contrib import admin
from .models import Category


class SubCategoryInline(admin.TabularInline):
    model = Category
    verbose_name = 'Subcategory'
    verbose_name_plural = 'Subcategories'
    fields = ['category_name', 'description']
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ('category_name', 'slug')
    inlines = [SubCategoryInline]


admin.site.register(Category, CategoryAdmin)
