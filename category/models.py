from django.db import models
from django.urls import reverse

# Create your models here.


class Category(models.Model):
    category_name = models.CharField(max_length=100, unique=True)
    # As the slugs need to be auto generated, used slug field without using CharField to slug.
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True)
    cat_image = models.ImageField(upload_to='photos/categories', blank=True)

# Django will automatically add 's' for the name to make it plural. To stop that This is used
    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_url(self):
        return reverse('products_by_category', args=[self.slug])

    def __str__(self):
        return self.category_name
