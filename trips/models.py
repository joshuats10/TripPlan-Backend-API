from django.contrib.auth.models import User
from django.db import models

import uuid

class UserProfile(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    device_id = models.UUIDField(null=True, blank=True)

    def __str__(self):
        if self.user:
            return str(self.user.username)
        else:
            return str(self.device_id)
        
class Trip(models.Model):
    trip_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(UserProfile, null=True, blank=True, on_delete=models.CASCADE)
    day = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return str(self.trip_id)

class Destination(models.Model):
    destination_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    travel_order = models.PositiveIntegerField(blank=True, null=True)
    arrival_time = models.DateTimeField(blank=True, null=True)
    departure_time = models.DateTimeField(blank=True, null=True)
    stay_time = models.DurationField(blank=True, null=True)
    next_destination_mode = models.CharField(max_length=200, blank=True, null=True)
    next_destination_travel_time = models.DurationField(blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['trip', 'travel_order']