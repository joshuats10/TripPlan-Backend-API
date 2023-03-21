import uuid
from django.db import models

# Create your models here.
class Places(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        db_index=True,
        editable=False
    )
    name = models.CharField(max_length=200)
    travel_order = models.PositiveIntegerField(blank=True, null=True)
    arrival_time = models.DateTimeField(blank=True, null=True)
    departure_time = models.DateTimeField(blank=True, null=True)
    stay_time = models.DurationField(blank=True, null=True)
    next_destination_mode = models.CharField(max_length=200, blank=True, null=True)
    next_destination_travel_time = models.DurationField(blank=True, null=True)

    def __str__(self):
        return self.name