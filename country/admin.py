import os
from django import forms
from django.contrib import admin
from .models import Country

# Define a ModelForm for Country model


class CountryForm(forms.ModelForm):
    # Load country names from a text file and use them as choices for the country_name field
    with open(os.path.join(os.path.dirname(__file__), 'countries.txt')) as f:
        countries = [line.strip() for line in f]
    COUNTRY_CHOICES = [(country, country) for country in countries]
    country_name = forms.ChoiceField(choices=COUNTRY_CHOICES)

    class Meta:
        model = Country
        fields = '__all__'


# Define CountryAdmin using the custom form
class CountryAdmin(admin.ModelAdmin):
    form = CountryForm
    list_display = ('country_name', 'formatted_shipping_cost')

    def formatted_shipping_cost(self, obj):
        return '$' + str(obj.shipping_cost)
    formatted_shipping_cost.short_description = 'Shipping Cost'


admin.site.register(Country, CountryAdmin)
