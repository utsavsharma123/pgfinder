import django_filters
from .models import Listing


class ListingFilter(django_filters.FilterSet):
    city = django_filters.CharFilter(lookup_expr='iexact')
    locality = django_filters.CharFilter(lookup_expr='icontains')
    gender_type = django_filters.ChoiceFilter(choices=Listing.GenderType.choices)
    meal_option = django_filters.ChoiceFilter(choices=Listing.MealOption.choices)
    status = django_filters.ChoiceFilter(choices=Listing.Status.choices)
    budget_min = django_filters.NumberFilter(field_name='price_single', lookup_expr='gte')
    budget_max = django_filters.NumberFilter(field_name='price_single', lookup_expr='lte')
    has_wifi = django_filters.BooleanFilter()
    has_ac = django_filters.BooleanFilter()
    has_parking = django_filters.BooleanFilter()
    has_geyser = django_filters.BooleanFilter()
    has_washing_machine = django_filters.BooleanFilter()
    has_cctv = django_filters.BooleanFilter()
    is_featured = django_filters.BooleanFilter()
    vacant_only = django_filters.BooleanFilter(field_name='vacant_beds', lookup_expr='gt', label='Show only vacant')

    class Meta:
        model = Listing
        fields = [
            'city', 'locality', 'gender_type', 'meal_option', 'status',
            'has_wifi', 'has_ac', 'has_parking', 'is_featured',
        ]
