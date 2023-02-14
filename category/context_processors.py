# This file will make dictionaries and pass it to the settings->template to be use this in any template

from .models import Category


def menu_links(request):
    links = Category.objects.all()
    return dict(links=links)
