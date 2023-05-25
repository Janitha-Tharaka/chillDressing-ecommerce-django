from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    # If someone typed accounts/ without typing dashboard, this will automatically send to dashboard
    path("", views.dashboard, name="dashboard"),
    path("activate/<uidb64>/<token>", views.activate, name="activate"),
    path("forgotPassword/", views.forgotPassword, name="forgotPassword"),
    path(
        "resetpassword_validate/<uidb64>/<token>",
        views.resetpassword_validate,
        name="resetpassword_validate",
    ),
    path("resetPassword/", views.resetPassword, name="resetPassword"),
    path("my_orders/", views.my_orders, name="my_orders"),
    path("edit_profile/", views.edit_profile, name="edit_profile"),
    path("change_password/", views.change_password, name="change_password"),
    path("order_detail/<int:order_id>/", views.order_detail, name="order_detail"),
    path("download_sales_data/", views.download_sales_data, name="download_sales_data"),
    path(
        "download_test_sales_data/",
        views.download_test_sales_data,
        name="download_test_sales_data",
    ),
    path("sales_prediction/", views.sales_prediction, name="sales_prediction"),
    path(
        "completed_sales_per_day_report/",
        views.completed_sales_per_day_report,
        name="completed_sales_per_day_report",
    ),
    path(
        "new_sales_per_day_report/",
        views.new_sales_per_day_report,
        name="new_sales_per_day_report",
    ),
    path(
        "sales_per_category_report/",
        views.sales_per_category_report,
        name="sales_per_category_report",
    ),
    path("cart_detail_report/", views.cart_detail_report, name="cart_detail_report"),
]
