from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from category.models import Category
from orders.models import Order, OrderProduct
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.views import _cart_id
from carts.models import Cart, CartItem
import requests

import csv
from django.conf import settings
from django.http import FileResponse
import os

# For Predictions
import pandas as pd
import matplotlib

matplotlib.use("Agg")  # Set the backend to non-interactive mode
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
from datetime import datetime

import io
import base64

# For Reports
from django.db.models import Sum
from django.contrib.auth.models import AnonymousUser


import os
from django.conf import settings


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Cleaned Data is the way of fetching the values from the form
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            phone_number = form.cleaned_data["phone_number"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            username = email.split("@")[0]
            while Account.objects.filter(username=username).exists():
                username += "-" + str(
                    Account.objects.filter(username__startswith=username).count() + 1
                )

            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
            )

            # Create user profile
            user_profile = UserProfile.objects.create(user=user)

            # Set user profile fields
            user_profile.phone_number = phone_number

            # Save profile picture
            profile_picture_path = os.path.join(
                settings.STATIC_ROOT, "images", "avatar", "user_image.png"
            )
            with open(profile_picture_path, "rb") as file:
                user_profile.profile_picture.save("user_image.png", file, save=True)

            user_profile.save()

            user.phone_number = phone_number
            user.save()

            # User Activation Progress
            # Current site is taken as when this is on working, the site URL will be changed
            current_site = get_current_site(request)
            mail_subject = "Activate your Account!"
            message = render_to_string(
                "accounts/account_verification_email.html",
                {
                    "user": user,
                    "domain": current_site,
                    # Encoding the primary key, So no one can see that!
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                },
            )
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            # messages.success(request, 'Thank you for registering with us! We have sent you a verification email!')
            return redirect("/accounts/login/?command=verification&email=" + email)
    else:
        form = RegistrationForm()

    context = {
        "form": form,
    }
    return render(request, "accounts/register.html", context)


def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        if email == "" or password == "":
            messages.error(request, "Username or Password is empty!")
            return redirect("login")

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()

                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        # Ass this variation is a query list, turned it into a list
                        product_variation.append(list(variation))

                    cart_item = CartItem.objects.filter(user=user)
                    # Checking the variations are exits
                    existing_variation_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        existing_variation_list.append(list(existing_variation))
                        id.append(item.id)

                    for pr in product_variation:
                        if pr in existing_variation_list:
                            index = existing_variation_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass
            auth.login(request, user)
            messages.success(request, "Logged in Successfully!")
            url = request.META.get("HTTP_REFERER")
            try:
                # Capturing the url which the user coming from (next=/cart/checkout)
                query = requests.utils.urlparse(url).query
                # print('query ', query)

                # Make a key and the values {'next' => '/cart/checkout'}
                params = dict(x.split("=") for x in query.split("&"))

                if "next" in params:
                    nextPage = params["next"]
                    return redirect(nextPage)
            except:
                return redirect("dashboard")
        else:
            messages.error(request, "Username or Password is wrong!")
            return redirect("login")
    return render(request, "accounts/login.html")


@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    messages.success(request, "Successfully Logged Out!")
    return redirect("login")


def activate(request, uidb64, token):
    # return HttpResponse('ok')
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulation! Your account is now activated.")
        return redirect("login")
    else:
        messages.error(request, "Invalid activation link")
        return redirect("register")


@login_required(login_url="login")
def dashboard(request):
    orders = Order.objects.order_by("-created_at").filter(
        user_id=request.user.id, is_ordered=True
    )
    orders_count = orders.count()

    try:
        userprofile = UserProfile.objects.get(user_id=request.user.id)
        if not userprofile.profile_picture:
            userprofile = None
    except UserProfile.DoesNotExist:
        userprofile = None

    context = {
        "orders_count": orders_count,
        "userprofile": userprofile,
    }
    return render(request, "accounts/dashboard.html", context)


def forgotPassword(request):
    if request.method == "POST":
        email = request.POST["email"]

        if email == "":
            messages.error(request, "Please enter an email address to continue!")
            return redirect("forgotPassword")
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Forgot Password Email
            # Curent site is taken as when this is on working, the site URL will be change
            current_site = get_current_site(request)
            mail_subject = "Reset Your Password!"
            message = render_to_string(
                "accounts/account_password_reset_email.html",
                {
                    "user": user,
                    "domain": current_site,
                    # Encoding the primary key, So noone can see that!
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                },
            )
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(
                request, "Password reset email has been sent to your email address!"
            )
            return redirect("login")

        else:
            messages.error(
                request, "Account Does not Exists! Try a valid email address!"
            )
            return redirect("forgotPassword")
    return render(request, "accounts/forgotPassword.html")


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.success(request, "Please reset your password")
        return redirect("resetPassword")
    else:
        messages.error(request, "This Link is Expired!")
        return redirect("register")


def resetPassword(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password == confirm_password:
            uid = request.session.get("uid")
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, "Password Reset Successful!")
            return redirect("login")

        else:
            messages.error(request, "Password Do Not Match!")
            return redirect("resetPassword")
    else:
        return render(request, "accounts/resetPassword.html")


@login_required(login_url="login")
def my_orders(request):
    # To get decending order, use - infront of th column name
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by(
        "-created_at"
    )

    context = {
        "orders": orders,
    }

    return render(request, "accounts/my_orders.html", context)


@login_required(login_url="login")
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=userprofile
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "User Profile has been updated Successfully!")
            return redirect("edit_profile")
    else:
        user_form = UserForm(instance=request.user)
        initial_profile = (
            {"profile_picture": userprofile.profile_picture}
            if userprofile.profile_picture
            else None
        )
        profile_form = UserProfileForm(instance=userprofile, initial=initial_profile)

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
        "userprofile": userprofile,
    }
    return render(request, "accounts/edit_profile.html", context)


@login_required(login_url="login")
def change_password(request):
    if request.method == "POST":
        current_password = request.POST["current_password"]
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request, "Password Updated Successfully!")
                return redirect("change_password")
            else:
                messages.error(request, "Please enter Correct Current Password!")
                return redirect("change_password")
        else:
            messages.error(request, "Password Does Not Match")
            return redirect("change_password")
    return render(request, "accounts/change_password.html")


@login_required(login_url="login")
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    sub_total = 0.00
    for i in order_detail:
        sub_total += i.total_price_per_product()
    context = {
        "order_detail": order_detail,
        "order": order,
        "sub_total": sub_total,
    }
    return render(request, "accounts/order_detail.html", context)


def download_sales_data(request):
    # Step 1: Fetch the latest data from the database
    current_year = datetime.now().year
    current_month = datetime.now().month

    orders = Order.objects.filter(status="Completed", is_recorded_for_prediction=0)

    data = []
    for order in orders:
        order_products = OrderProduct.objects.filter(order=order)
        for order_product in order_products:
            product = order_product.product
            category_name = product.category.category_name
            quantity = order_product.quantity

            row = {
                "year": current_year,
                "month": current_month,
                "category": category_name,
                "units_sold": quantity,
            }

            data.append(row)

    # Step 2: Update the CSV file
    sales_data_path = os.path.join(settings.BASE_DIR, "static", "sales_data.csv")

    updated_rows = 0
    with open(sales_data_path, "r+", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

        for i, row in enumerate(rows):
            if (
                row["year"] == str(current_year)
                and row["month"] == str(current_month)
                and row["category"] in [item["category"] for item in data]
            ):
                category_data = next(
                    item for item in data if item["category"] == row["category"]
                )
                row["units_sold"] = str(
                    int(row["units_sold"]) + category_data["units_sold"]
                )
                rows[i] = row
                updated_rows += 1

        file.seek(0)
        writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Step 3: Check if any rows were updated
    if updated_rows == 0:
        error_message = "No matching rows found in the CSV file for update."
        # You can handle this error message as per your application's requirements

    # Step 4: Download the updated CSV file
    sales_data_file = open(sales_data_path, "rb")
    response = FileResponse(sales_data_file)
    response["Content-Disposition"] = "attachment; filename=sales_data.csv"
    response["Content-Type"] = "text/csv"

    return response


def download_test_sales_data(request):
    sales_data_path = os.path.join(settings.BASE_DIR, "static", "sales_data.csv")
    sales_data_file = open(sales_data_path, "rb")
    response = FileResponse(sales_data_file)
    return response


@login_required(login_url="login")
def sales_prediction(request):
    if request.method == "POST":
        category_name = request.POST.get("category")
        if category_name:
            # Handle the uploaded CSV file
            csv_file = request.FILES["csv_file"]

            # Check the file extension
            if not csv_file.name.endswith(".csv"):
                # Display an error message indicating an invalid file type
                error_message = "Invalid file type. Please choose a CSV file."
                messages.error(request, error_message)
                return redirect("/accounts/sales_prediction/")

            df = pd.read_csv(csv_file)

            # Filter the dataset for the selected category
            df_selected_category = df[df["category"] == category_name]

            if df_selected_category.empty:
                messages.error(request, "No data found for the selected category.")
                return redirect("/accounts/sales_prediction/")

            # Convert categorical variables into dummy/indicator variables
            df_encoded = pd.get_dummies(
                df_selected_category, columns=["month", "season"]
            )

            # Encode the 'category' column
            label_encoder = LabelEncoder()
            df_encoded["category_encoded"] = label_encoder.fit_transform(
                df_encoded["category"]
            )

            season_mapping = {
                12: "Winter",
                1: "Winter",
                2: "Winter",
                3: "Spring",
                4: "Spring",
                5: "Spring",
                6: "Summer",
                7: "Summer",
                8: "Summer",
                9: "Autumn",
                10: "Autumn",
                11: "Autumn",
            }

            # Separate the features (X) and the target variable (y)
            X = df_encoded.drop(["units_sold", "category"], axis=1)
            y = df_encoded["units_sold"]

            # Train a linear regression model
            model = LinearRegression()
            model.fit(X, y)

            # Get the current month and year
            current_month = datetime.now().month
            current_year = datetime.now().year

            # Define a function to generate the features for a given month
            def generate_features(month, year):
                if month > 12:
                    month = month % 12
                    year += 1

                data = pd.DataFrame(
                    {"year": [year], "month": [month], "category": [category_name]}
                )

                data["season"] = season_mapping[month]
                data["specific_holidays"] = (
                    3
                    if month == 12
                    else 1
                    if month == 1
                    else 2
                    if month in [3, 4, 5]
                    else 0
                )

                data_encoded = pd.get_dummies(data, columns=["month", "season"])
                data_encoded["category_encoded"] = label_encoder.transform(
                    data_encoded["category"]
                )
                data_encoded = data_encoded.reindex(columns=X.columns, fill_value=0)

                return data_encoded

            # Prepare data for the line chart
            historical_data = (
                df_selected_category.groupby(["year", "month"])["units_sold"]
                .sum()
                .reset_index()
            )
            historical_data["date"] = pd.to_datetime(
                historical_data[["year", "month"]].assign(day=1)
            )

            if current_month in [1, 2, 3, 4]:
                # Get last year's data if the prediction starts from January, February, March, or April
                last_year_data = df_selected_category[
                    df_selected_category["year"] == current_year - 1
                ]
                historical_data = pd.concat([last_year_data, historical_data])
            else:
                # Consider only the current year's data
                historical_data = historical_data[
                    historical_data["year"] == current_year
                ]

            # Make predictions for the current month and the next three months
            units_sold_current_month = model.predict(
                generate_features(current_month, current_year)
            )
            units_sold_next_month = model.predict(
                generate_features(current_month + 1, current_year)
            )
            units_sold_month_after_next = model.predict(
                generate_features(current_month + 2, current_year)
            )
            units_sold_third_month = model.predict(
                generate_features(current_month + 3, current_year)
            )

            predicted_data = pd.DataFrame(
                {
                    "date": pd.to_datetime(
                        [
                            f"{current_year}-{current_month}-{1}",
                            f"{current_year}-{current_month+1}-{1}",
                            f"{current_year}-{current_month+2}-{1}",
                            f"{current_year}-{current_month+3}-{1}",
                        ]
                    ),
                    "units_sold": [
                        units_sold_current_month,
                        units_sold_next_month,
                        units_sold_month_after_next,
                        units_sold_third_month,
                    ],
                }
            )

            # Generate the plot
            plt.figure(figsize=(10, 6))
            # Plotting code goes here...

            # Plot the line chart
            plt.figure(figsize=(10, 6))
            plt.plot(
                historical_data["date"],
                historical_data["units_sold"],
                label="Historical",
                marker="o",
            )
            plt.plot(
                predicted_data["date"],
                predicted_data["units_sold"],
                label="Predicted",
                marker="o",
            )
            plt.xlabel("Year-Month")
            plt.ylabel("Units Sold")
            plt.title(f"Units Sold for {category_name} (Historical and Predicted)")
            plt.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()

            # Render the plot to an image buffer
            buffer = io.BytesIO()
            plt.savefig(buffer, format="png")
            buffer.seek(0)

            # Convert the image buffer to a base64 encoded string
            image_data = base64.b64encode(buffer.getvalue()).decode("utf-8")

            # Prepare the data for the table
            table_data = [
                ("Current Month", units_sold_current_month),
                ("Next Month", units_sold_next_month),
                ("Month After Next", units_sold_month_after_next),
                ("Third Month", units_sold_third_month),
            ]

            # Pass the image data and table data to the template
            context = {
                "table_data": table_data,
                "image_data": image_data,
            }

            return render(request, "sales_prediction/prediction_output.html", context)

    categories = Category.objects.all()
    context = {"categories": categories}
    return render(request, "sales_prediction/csv_upload.html", context)


@login_required(login_url="login")
def completed_sales_per_day_report(request):
    # Retrieve completed orders
    completed_orders = Order.objects.filter(status="Completed", is_ordered=True)

    # Group orders by day and calculate total sales for each day
    sales_per_day = completed_orders.values("created_at").annotate(
        total_sales=Sum("order_total")
    )

    context = {"sales_per_day": sales_per_day}

    return render(request, "reports/completed_sales_per_day_report.html", context)


@login_required(login_url="login")
def new_sales_per_day_report(request):
    # Retrieve completed orders
    completed_orders = Order.objects.filter(status="New", is_ordered=True)

    # Group orders by day and calculate total sales for each day
    new_sales_per_day = completed_orders.values("created_at").annotate(
        total_sales=Sum("order_total")
    )

    context = {"new_sales_per_day": new_sales_per_day}

    return render(request, "reports/new_sales_per_day_report.html", context)


@login_required(login_url="login")
def sales_per_category_report(request):
    # Retrieve completed orders
    completed_orders = Order.objects.filter(status="Completed", is_ordered=True)

    # Retrieve order products for completed orders
    order_products = OrderProduct.objects.filter(order__in=completed_orders)

    # Group order products by category and calculate total sales for each category
    sales_per_category = order_products.values(
        "product__category__category_name"
    ).annotate(total_sales=Sum("quantity"))

    context = {"sales_per_category": sales_per_category}
    return render(request, "reports/sales_per_category_report.html", context)


@login_required(login_url="login")
def cart_detail_report(request):
    carts = Cart.objects.all()

    cart_data = []
    for cart in carts:
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        total_value = cart_items.aggregate(total=Sum("quantity"))["total"]

        if cart_items.exists():
            user_name = (
                cart_items.first().user.full_name()
                if cart_items.first().user
                else "Non User"
            )

            cart_data.append(
                {
                    "user_name": user_name,
                    "cart_id": cart.cart_id,
                    "date_added": cart.date_added,
                    "products": cart_items,
                    "total_value": total_value,
                }
            )

    context = {
        "cart_data": cart_data,
    }

    return render(request, "reports/cart_detail_report.html", context)
