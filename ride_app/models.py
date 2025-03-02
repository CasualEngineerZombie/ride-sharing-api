from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        RIDER = "rider", "Rider"
        ADMIN = "admin", "Admin"
        
    id_user = models.AutoField(primary_key=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER   
    )
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Ride(models.Model):
    id_ride = models.AutoField(primary_key=True)
    status = models.CharField(max_length=50)
    id_rider = models.ForeignKey(
        User, related_name="rider_rides", on_delete=models.CASCADE
    )
    id_driver = models.ForeignKey(
        User, related_name="driver_rides", on_delete=models.CASCADE
    )
    pickup_latitude = models.FloatField()
    pickup_longitude = models.FloatField()
    dropoff_latitude = models.FloatField()
    dropoff_longitude = models.FloatField()
    pickup_time = models.DateTimeField()

    def __str__(self):
        return f"Ride {self.id_ride}"


class RideEvent(models.Model):
    id_ride_event = models.AutoField(primary_key=True)
    id_ride = models.ForeignKey(
        Ride, related_name="ride_events", on_delete=models.CASCADE
    )
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"RideEvent {self.id_ride_event} for Ride {self.id_ride.id_ride}"
