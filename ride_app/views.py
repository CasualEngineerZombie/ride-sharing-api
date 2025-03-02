from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.db.models import F, ExpressionWrapper, FloatField
from django.db.models.functions import Sqrt, Power

from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination

from .models import Ride, RideEvent
from .serializers import RideSerializer
from .permissions import IsAdminRole
from .filters import RideFilter
import django_filters.rest_framework


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class RideViewSet(viewsets.ModelViewSet):
    serializer_class = RideSerializer
    permission_classes = [IsAdminRole]
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    filterset_class = RideFilter
    ordering_fields = ["pickup_time", "distance"]

    def get_queryset(self): 

        now = timezone.now()
        last_24_hours = now - timedelta(days=1)

        # Prefetch only today's ride events into an attribute 'todays_ride_events'
        todays_events_prefetch = models.Prefetch(
            "ride_events",
            queryset=RideEvent.objects.filter(created_at__gte=last_24_hours),
            to_attr="todays_ride_events",
        )

        queryset = (
            Ride.objects.all()
            .select_related("id_rider", "id_driver")
            .prefetch_related(todays_events_prefetch)
        )

        # If sorting by distance is requested, expect query parameters: ordering=distance, lat, and lng.
        ordering = self.request.query_params.get("ordering", "")
        lat = self.request.query_params.get("lat")
        lng = self.request.query_params.get("lng")
        if "distance" in ordering and lat and lng:
            try:
                lat = float(lat)
                lng = float(lng)
                queryset = queryset.annotate(
                    distance=ExpressionWrapper(
                        Sqrt(
                            Power(F("pickup_latitude") - lat, 2)
                            + Power(F("pickup_longitude") - lng, 2)
                        ),
                        output_field=FloatField(),
                    )
                )
            except ValueError:
                pass  # In case of conversion error, ignore distance ordering.
        return queryset
