from django.contrib import admin
from sales_prediction.models import SalesPrediction
from sales_prediction.forms import SalesPredictionForm
from sales_prediction.prediction import (
    perform_prediction,
)  # Assuming you have a separate module for prediction logic
