from django.db import models

# Create your models here.


class Country(models.Model):
    country_name = models.CharField(max_length=255, unique=True)
    shipping_cost = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        verbose_name = 'country'
        verbose_name_plural = 'countries'

    def __str__(self):
        return self.country_name
