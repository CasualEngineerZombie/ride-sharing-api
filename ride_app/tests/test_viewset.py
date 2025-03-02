from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from ride_app.models import User, Ride, RideEvent


class RideViewSetTests(APITestCase):

    def setUp(self):
        # Create an admin user
        self.admin_user = User.objects.create_user(
            username="admin",
            password="password123",
            first_name="Admin",
            last_name="User",
            role=User.Role.ADMIN,
            phone_number="1234567890",
        )
        # Create a regular (non-admin) user
        self.regular_user = User.objects.create_user(
            username="regular",
            password="password123",
            first_name="Regular",
            last_name="User",
            role=User.Role.CUSTOMER,
            phone_number="0987654321",
        )
        now = timezone.now()
        # Create two rides with different statuses and pickup times
        self.ride1 = Ride.objects.create(
            status="pickup",
            id_rider=self.admin_user,
            id_driver=self.admin_user,
            pickup_latitude=10.0,
            pickup_longitude=20.0,
            dropoff_latitude=30.0,
            dropoff_longitude=40.0,
            pickup_time=now - timedelta(hours=1),
        )
        self.ride2 = Ride.objects.create(
            status="dropoff",
            id_rider=self.admin_user,
            id_driver=self.admin_user,
            pickup_latitude=15.0,
            pickup_longitude=25.0,
            dropoff_latitude=35.0,
            dropoff_longitude=45.0,
            pickup_time=now - timedelta(hours=2),
        )
        # Create a recent RideEvent (within the last 24 hours) for ride1
        self.ride_event_recent = RideEvent.objects.create(
            id_ride=self.ride1,
            description="Status changed to pickup",
            created_at=now - timedelta(minutes=30),
        )
        # Create an old RideEvent (older than 24 hours) for ride2
        self.ride_event_old = RideEvent.objects.create(
            id_ride=self.ride2,
            description="Status changed to dropoff",
            created_at=now - timedelta(days=2),
        )
        self.client = APIClient()

    def test_admin_can_access_ride_list(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("ride-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Expecting two rides (plus one pagination query)
        self.assertEqual(len(response.data["results"]), 2)
        # Verify that only ride1 has recent events pre-fetched
        for ride in response.data["results"]:
            if ride["id_ride"] == self.ride1.id_ride:
                self.assertGreater(len(ride["todays_ride_events"]), 0)
            else:
                self.assertEqual(len(ride["todays_ride_events"]), 0)

    def test_non_admin_cannot_access_ride_list(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse("ride-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filtering_by_status(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("ride-list")
        # Filter for rides with status "pickup"
        response = self.client.get(url, {"status": "pickup"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["status"], "pickup")

    def test_ordering_by_pickup_time(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("ride-list")
        # Ascending order (older first): ride2 then ride1
        response = self.client.get(url, {"ordering": "pickup_time"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        times = [parse_datetime(ride["pickup_time"]) for ride in results]
        self.assertTrue(times[0] < times[1])
        # Descending order (newer first): ride1 then ride2
        response = self.client.get(url, {"ordering": "-pickup_time"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        times = [parse_datetime(ride["pickup_time"]) for ride in results]
        self.assertTrue(times[0] > times[1])

    def test_ordering_by_distance(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("ride-list")
        # Use a reference point for distance calculation
        lat = 10.0
        lng = 20.0
        # Ascending: closest first
        response = self.client.get(
            url, {"ordering": "distance", "lat": lat, "lng": lng}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]

        def calc_distance(ride):
            return (
                (ride["pickup_latitude"] - lat) ** 2
                + (ride["pickup_longitude"] - lng) ** 2
            ) ** 0.5

        distances = [calc_distance(ride) for ride in results]
        self.assertEqual(distances, sorted(distances))
        # Descending: furthest first
        response = self.client.get(
            url, {"ordering": "-distance", "lat": lat, "lng": lng}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        distances_desc = [calc_distance(ride) for ride in results]
        self.assertEqual(distances_desc, sorted(distances_desc, reverse=True))
