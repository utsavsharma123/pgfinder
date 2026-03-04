from django.urls import path
from .views import SearchView, CitySuggestView

urlpatterns = [
    path('', SearchView.as_view(), name='search'),
    path('suggest/', CitySuggestView.as_view(), name='search-suggest'),
]
