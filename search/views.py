"""
Search app — Advanced search with geo-distance support.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Q
from listings.models import Listing
from listings.serializers import ListingListSerializer
from listings.filters import ListingFilter
from rest_framework.pagination import PageNumberPagination
import math


def haversine_distance(lat1, lon1, lat2, lon2):
    """Return distance in km between two lat/lon points."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


class SearchPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50


@extend_schema(
    tags=['Search'],
    parameters=[
        OpenApiParameter('city', OpenApiTypes.STR, description='City name (required)'),
        OpenApiParameter('locality', OpenApiTypes.STR, description='Locality/area name'),
        OpenApiParameter('budget_min', OpenApiTypes.INT, description='Minimum budget (₹/month)'),
        OpenApiParameter('budget_max', OpenApiTypes.INT, description='Maximum budget (₹/month)'),
        OpenApiParameter('gender_type', OpenApiTypes.STR, description='male | female | coed'),
        OpenApiParameter('meal_option', OpenApiTypes.STR, description='no_meals | breakfast | all_meals'),
        OpenApiParameter('has_wifi', OpenApiTypes.BOOL),
        OpenApiParameter('has_ac', OpenApiTypes.BOOL),
        OpenApiParameter('has_parking', OpenApiTypes.BOOL),
        OpenApiParameter('lat', OpenApiTypes.FLOAT, description='User latitude for distance filter'),
        OpenApiParameter('lng', OpenApiTypes.FLOAT, description='User longitude for distance filter'),
        OpenApiParameter('radius_km', OpenApiTypes.FLOAT, description='Search radius in km (default: 10)'),
        OpenApiParameter('sort', OpenApiTypes.STR, description='price_asc | price_desc | newest | distance'),
    ]
)
class SearchView(APIView):
    """
    Full-text + filter search for PG listings.
    Supports geo-distance filtering via lat/lng/radius_km.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        qs = Listing.objects.filter(status='active').select_related('owner').prefetch_related('photos')

        city = request.query_params.get('city')
        if city:
            qs = qs.filter(city__iexact=city)

        locality = request.query_params.get('locality')
        if locality:
            qs = qs.filter(locality__icontains=locality)

        budget_min = request.query_params.get('budget_min')
        budget_max = request.query_params.get('budget_max')
        if budget_min:
            qs = qs.filter(Q(price_single__gte=budget_min) | Q(price_double__gte=budget_min) | Q(price_triple__gte=budget_min))
        if budget_max:
            qs = qs.filter(Q(price_single__lte=budget_max) | Q(price_double__lte=budget_max) | Q(price_triple__lte=budget_max))

        gender_type = request.query_params.get('gender_type')
        if gender_type:
            qs = qs.filter(gender_type=gender_type)

        meal_option = request.query_params.get('meal_option')
        if meal_option:
            qs = qs.filter(meal_option=meal_option)

        for amenity in ['has_wifi', 'has_ac', 'has_parking', 'has_geyser', 'has_washing_machine']:
            val = request.query_params.get(amenity)
            if val and val.lower() == 'true':
                qs = qs.filter(**{amenity: True})

        # Geo distance filter (client-side haversine for SQLite; use PostGIS in production)
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius_km = float(request.query_params.get('radius_km', 10))

        results = list(qs)

        if lat and lng:
            user_lat, user_lng = float(lat), float(lng)
            filtered = []
            for listing in results:
                if listing.latitude and listing.longitude:
                    dist = haversine_distance(user_lat, user_lng, float(listing.latitude), float(listing.longitude))
                    if dist <= radius_km:
                        listing._distance_km = round(dist, 2)
                        filtered.append(listing)
            results = filtered

        # Sorting
        sort = request.query_params.get('sort', 'newest')
        if sort == 'price_asc':
            results.sort(key=lambda x: min(p for p in [x.price_single, x.price_double, x.price_triple] if p) if any([x.price_single, x.price_double, x.price_triple]) else 0)
        elif sort == 'price_desc':
            results.sort(key=lambda x: min(p for p in [x.price_single, x.price_double, x.price_triple] if p) if any([x.price_single, x.price_double, x.price_triple]) else 0, reverse=True)
        elif sort == 'distance' and lat and lng:
            results.sort(key=lambda x: getattr(x, '_distance_km', 9999))
        else:
            results.sort(key=lambda x: x.created_at, reverse=True)

        paginator = SearchPagination()
        page = paginator.paginate_queryset(results, request)
        serializer = ListingListSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


@extend_schema(tags=['Search'])
class CitySuggestView(APIView):
    """Return list of cities and localities for autocomplete."""
    permission_classes = [AllowAny]

    def get(self, request):
        q = request.query_params.get('q', '')
        cities = (
            Listing.objects.filter(status='active', city__icontains=q)
            .values_list('city', flat=True)
            .distinct()[:10]
        )
        localities = (
            Listing.objects.filter(status='active', locality__icontains=q)
            .values_list('locality', flat=True)
            .distinct()[:10]
        )
        return Response({'cities': list(cities), 'localities': list(localities)})
