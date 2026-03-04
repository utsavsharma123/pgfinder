from django.urls import path
from .views import PlanListView, MySubscriptionView, CreateOrderView, VerifyPaymentView

urlpatterns = [
    path('plans/', PlanListView.as_view(), name='subscription-plans'),
    path('my/', MySubscriptionView.as_view(), name='my-subscription'),
    path('create-order/', CreateOrderView.as_view(), name='create-order'),
    path('verify-payment/', VerifyPaymentView.as_view(), name='verify-payment'),
]
