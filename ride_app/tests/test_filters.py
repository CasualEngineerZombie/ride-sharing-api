from django.test import TestCase
from ride_app.models import Ride, User
from ride_app.filters import RideFilter

class RideFilterTestCase(TestCase):
    def setUp(self):
        # Create two users with different emails.
        self.user1 = User.objects.create_user(
            username="alice",
            password="password123",
            first_name="Alice",
            last_name="Wonderland",
            email="alice@example.com",
            role=User.Role.RIDER,
            phone_number="1111111111"
        )
        self.user2 = User.objects.create_user(
            username="bob",
            password="password123",
            first_name="Bob",
            last_name="Builder",
            email="bob@example.com",
            role=User.Role.RIDER,
            phone_number="2222222222"
        )

        # Create rides with different statuses and rider associations.
        # Ride 1: status 'pickup', rider = user1
        self.ride1 = Ride.objects.create(
            status="pickup",
            id_rider=self.user1,
            id_driver=self.user2,
            pickup_latitude=10.0,
            pickup_longitude=20.0,
            dropoff_latitude=30.0,
            dropoff_longitude=40.0,
            pickup_time="2025-03-01T10:00:00Z"
        )
        # Ride 2: status 'dropoff', rider = user2
        self.ride2 = Ride.objects.create(
            status="dropoff",
            id_rider=self.user2,
            id_driver=self.user1,
            pickup_latitude=11.0,
            pickup_longitude=21.0,
            dropoff_latitude=31.0,
            dropoff_longitude=41.0,
            pickup_time="2025-03-02T11:00:00Z"
        )
        # Ride 3: status 'pickup', rider = user2
        self.ride3 = Ride.objects.create(
            status="pickup",
            id_rider=self.user2,
            id_driver=self.user1,
            pickup_latitude=12.0,
            pickup_longitude=22.0,
            dropoff_latitude=32.0,
            dropoff_longitude=42.0,
            pickup_time="2025-03-03T12:00:00Z"
        )

    def test_filter_by_status(self):
        # Filtering rides with status 'pickup' should return ride1 and ride3.
        data = {'status': 'pickup'}
        filtered = RideFilter(data=data, queryset=Ride.objects.all())
        qs = filtered.qs
        self.assertEqual(qs.count(), 2)
        for ride in qs:
            self.assertEqual(ride.status.lower(), 'pickup')

    def test_filter_by_rider_email(self):
        # Filtering by a rider_email containing 'alice' should return ride1.
        data = {'rider_email': 'alice'}
        filtered = RideFilter(data=data, queryset=Ride.objects.all())
        qs = filtered.qs
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().id_rider.email, "alice@example.com")

    def test_combined_filters(self):
        # Combining filters for status 'pickup' and rider_email containing 'bob'
        # should return ride3, since ride3 is 'pickup' and its rider (user2) has email 'bob@example.com'.
        data = {'status': 'pickup', 'rider_email': 'bob'}
        filtered = RideFilter(data=data, queryset=Ride.objects.all())
        qs = filtered.qs
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().id_rider.email, "bob@example.com")
