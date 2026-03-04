from django.urls import path
from .views import (
    ListingListCreateView, ListingDetailView,
    ListingPhotoView, ListingStatusToggleView,
    WishlistView, WishlistDetailView,
)

urlpatterns = [
    path('', ListingListCreateView.as_view(), name='listing-list'),
    path('<int:pk>/', ListingDetailView.as_view(), name='listing-detail'),
    path('<int:pk>/photos/', ListingPhotoView.as_view(), name='listing-photos'),
    path('<int:pk>/status/', ListingStatusToggleView.as_view(), name='listing-status'),
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('wishlist/<int:pk>/', WishlistDetailView.as_view(), name='wishlist-detail'),
]
