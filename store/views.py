from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ReviewRating, ProductGallery
from category.models import Category
from carts.views import _cart_id
from django.http import HttpResponse
from carts.models import CartItem
from django.db.models import Q

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct
# Create your views here.


def store(request, category_slug=None):
    categories = None
    products = None
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(
            category=categories, is_available=True)

        # This is for pagination
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)

        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        # This is for pagination
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    context = {
        'products': paged_products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    # category__slug means in going to the product->category and then go to the category table and take slug of category
    try:
        single_product = Product.objects.get(
            category__slug=category_slug, slug=product_slug)
        # Two __ are used to get the cart_id through cart as cart is a foreignkey. Check in carts model
        in_cart = CartItem.objects.filter(
            cart__cart_id=_cart_id(request), product=single_product).exists()

    except Exception as e:
        raise e

    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(
                user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None

    else:
        orderproduct = None

    # Get all the reviews
    reviews = ReviewRating.objects.filter(
        product_id=single_product.id, status=True)

    # Get the product images
    product_gallery = ProductGallery.objects.filter(
        product_id=single_product.id)

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'product_gallery': product_gallery,
    }
    return render(request, 'store/product_detail.html', context)


def search(request):
    products = ''
    product_count = 0
    empty_string = 0
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by(
                '-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
        else:
            empty_string = 1

    context = {
        'products': products,
        'product_count': product_count,
        'empty_string': empty_string
    }
    return render(request, 'store/store.html', context)


def submit_review(request, product_id):
    # This will store the previous url
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(
                user__id=request.user.id, product__id=product_id)
            # Instance will update the review if there is a review
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(
                request, 'Thank you for Reviewing US! Your Review Updated!')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(
                    request, 'Thank you for Reviewing US! Your Review submitted!')
                return redirect(url)
