from rest_framework import serializers
from .models import User, Ride, RideEvent


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id_user", "role", "first_name", "last_name", "email", "phone_number"]


class RideEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideEvent
        fields = ["id_ride_event", "description", "created_at"]


class RideSerializer(serializers.ModelSerializer):
    id_rider = UserSerializer(read_only=True)
    id_driver = UserSerializer(read_only=True)
    todays_ride_events = serializers.SerializerMethodField()

    class Meta:
        model = Ride
        fields = [
            "id_ride",
            "status",
            "id_rider",
            "id_driver",
            "pickup_latitude",
            "pickup_longitude",
            "dropoff_latitude",
            "dropoff_longitude",
            "pickup_time",
            "todays_ride_events",
        ]

    def get_todays_ride_events(self, obj):
        # This expects that the queryset has prefetched ride_events from the last 24 hours
        ride_events = getattr(obj, "todays_ride_events", [])
        return RideEventSerializer(ride_events, many=True).data
