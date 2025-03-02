from django.test import TestCase
from django.utils import timezone
from ride_app.models import User, Ride, RideEvent
from ride_app.serializers import UserSerializer, RideEventSerializer, RideSerializer


class UserSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="password123",
            first_name="Alice",
            last_name="Smith",
            email="alice@example.com",
            role=User.Role.ADMIN,
            phone_number="1234567890",
        )

    def test_user_serializer(self):
        serializer = UserSerializer(instance=self.user)
        data = serializer.data
        self.assertEqual(data["id_user"], self.user.id_user)
        self.assertEqual(data["role"], self.user.role)
        self.assertEqual(data["first_name"], self.user.first_name)
        self.assertEqual(data["last_name"], self.user.last_name)
        self.assertEqual(data["email"], self.user.email)
        self.assertEqual(data["phone_number"], self.user.phone_number)


class RideEventSerializerTest(TestCase):
    def setUp(self):
        # Create a dummy user and ride to associate with the event.
        self.user = User.objects.create_user(
            username="eventuser",
            password="password123",
            first_name="Bob",
            last_name="Jones",
            email="bob@example.com",
            role=User.Role.ADMIN,
            phone_number="5555555555",
        )
        self.ride = Ride.objects.create(
            status="pickup",
            id_rider=self.user,
            id_driver=self.user,
            pickup_latitude=10.0,
            pickup_longitude=20.0,
            dropoff_latitude=30.0,
            dropoff_longitude=40.0,
            pickup_time=timezone.now(),
        )
        self.ride_event = RideEvent.objects.create(
            id_ride=self.ride, description="Test ride event", created_at=timezone.now()
        )

    def test_ride_event_serializer(self):
        serializer = RideEventSerializer(instance=self.ride_event)
        data = serializer.data
        self.assertEqual(data["id_ride_event"], self.ride_event.id_ride_event)
        self.assertEqual(data["description"], self.ride_event.description)
        # Verify that created_at is serialized (a non-empty string)
        self.assertTrue("T" in data["created_at"])


class RideSerializerTest(TestCase):
    def setUp(self):
        # Create two users for rider and driver.
        self.rider = User.objects.create_user(
            username="rideruser",
            password="password123",
            first_name="Rider",
            last_name="One",
            email="rider@example.com",
            role=User.Role.RIDER,
            phone_number="1112223333",
        )
        self.driver = User.objects.create_user(
            username="driveruser",
            password="password123",
            first_name="Driver",
            last_name="One",
            email="driver@example.com",
            role=User.Role.ADMIN,
            phone_number="4445556666",
        )
        self.ride = Ride.objects.create(
            status="en-route",
            id_rider=self.rider,
            id_driver=self.driver,
            pickup_latitude=10.0,
            pickup_longitude=20.0,
            dropoff_latitude=30.0,
            dropoff_longitude=40.0,
            pickup_time=timezone.now(),
        )
        # Create a recent ride event (within last 24 hours)
        self.recent_event = RideEvent.objects.create(
            id_ride=self.ride,
            description="Recent event",
            created_at=timezone.now() - timezone.timedelta(hours=1),
        )
        # Simulate the prefetch by setting the attribute manually.
        self.ride.todays_ride_events = [self.recent_event]

    def test_ride_serializer(self):
        serializer = RideSerializer(instance=self.ride)
        data = serializer.data
        self.assertEqual(data["id_ride"], self.ride.id_ride)
        self.assertEqual(data["status"], self.ride.status)
        # Verify nested serialization for rider and driver
        self.assertEqual(data["id_rider"]["id_user"], self.rider.id_user)
        self.assertEqual(data["id_driver"]["id_user"], self.driver.id_user)
        # Verify that today's ride events are correctly serialized.
        self.assertEqual(len(data["todays_ride_events"]), 1)
        event_data = data["todays_ride_events"][0]
        self.assertEqual(event_data["id_ride_event"], self.recent_event.id_ride_event)
        self.assertEqual(event_data["description"], self.recent_event.description)
