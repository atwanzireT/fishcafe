from django.db import models


from django.db import models

class Reservation(models.Model):
    EVENT_TYPES = [
        ('birthday', 'Birthday'),
        ('wedding', 'Wedding'),
        ('other', 'Other'),
    ]

    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    name = models.CharField(max_length=100)  # Name of the person booking
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    event_date = models.DateField()
    number_of_guests = models.PositiveIntegerField()
    special_requests = models.TextField(blank=True, null=True)  # Optional requests or preferences

    def __str__(self):
        return f"{self.event_type.capitalize()} - {self.name} on {self.event_date}"


# Create your models here.
