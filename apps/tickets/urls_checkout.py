from django.urls import path

from apps.tickets.views import CheckoutView

urlpatterns = [
    path("", CheckoutView.as_view(), name="checkout"),
]
