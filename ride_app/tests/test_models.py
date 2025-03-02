from django.test import TestCase
from django.utils import timezone
from ride_app.models import User, Ride, RideEvent

class UserModelTest(TestCase):
    def test_user_str(self):
        user = User.objects.create_user(
            username="testuser",
            password="password123",
            first_name="John",
            last_name="Doe",
            role=User.Role.ADMIN,
            phone_number="1234567890"
        )
        self.assertEqual(str(user), "John Doe")


class RideModelTest(TestCase):
    def setUp(self):
        self.rider = User.objects.create_user(
            username="rider",
            password="password123",
            first_name="Rider",
            last_name="Test",
            role=User.Role.RIDER,
            phone_number="1112223333"
        )
        self.driver = User.objects.create_user(
            username="driver",
            password="password123",
            first_name="Driver",
            last_name="Test",
            role=User.Role.ADMIN,
            phone_number="4445556666"
        )
    
    def test_ride_str(self):
        ride = Ride.objects.create(
            status="en-route",
            id_rider=self.rider,
            id_driver=self.driver,
            pickup_latitude=10.0,
            pickup_longitude=20.0,
            dropoff_latitude=30.0,
            dropoff_longitude=40.0,
            pickup_time=timezone.now()
        )
        self.assertEqual(str(ride), f"Ride {ride.id_ride}")

    def test_ride_relationships(self):
        # Create a ride and ensure the related users are correctly associated.
        ride = Ride.objects.create(
            status="pickup",
            id_rider=self.rider,
            id_driver=self.driver,
            pickup_latitude=10.0,
            pickup_longitude=20.0,
            dropoff_latitude=30.0,
            dropoff_longitude=40.0,
            pickup_time=timezone.now()
        )
        self.assertEqual(ride.id_rider, self.rider)
        self.assertEqual(ride.id_driver, self.driver)


class RideEventModelTest(TestCase):
    def setUp(self):
        self.rider = User.objects.create_user(
            username="rider2",
            password="password123",
            first_name="Rider2",
            last_name="Test",
            role=User.Role.RIDER,
            phone_number="1112223333"
        )
        self.driver = User.objects.create_user(
            username="driver2",
            password="password123",
            first_name="Driver2",
            last_name="Test",
            role=User.Role.ADMIN,
            phone_number="4445556666"
        )
        self.ride = Ride.objects.create(
            status="pickup",
            id_rider=self.rider,
            id_driver=self.driver,
            pickup_latitude=10.0,
            pickup_longitude=20.0,
            dropoff_latitude=30.0,
            dropoff_longitude=40.0,
            pickup_time=timezone.now()
        )
    
    def test_rideevent_str(self):
        ride_event = RideEvent.objects.create(
            id_ride=self.ride,
            description="Status changed to pickup",
            created_at=timezone.now()
        )
        expected_str = f"RideEvent {ride_event.id_ride_event} for Ride {self.ride.id_ride}"
        self.assertEqual(str(ride_event), expected_str)

    def test_ride_events_relationship(self):
        # Create multiple events for the same ride
        event1 = RideEvent.objects.create(
            id_ride=self.ride,
            description="Status changed to pickup",
            created_at=timezone.now()
        )
        event2 = RideEvent.objects.create(
            id_ride=self.ride,
            description="Status changed to dropoff",
            created_at=timezone.now()
        )
        # Check that the ride has two related events.
        events = self.ride.ride_events.all()
        self.assertEqual(events.count(), 2)
        self.assertIn(event1, events)
        self.assertIn(event2, events)
