from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

class OtherPackage(models.Model):
    SERVICE_TYPES = [
        ('Conference', 'Conference Room'),
        ('Gardens', 'Gardens'),
        ('Gym', 'Gym Access'),
        ('Laundry', 'Laundry Service'),
        ('Massage', 'Massage Therapy'),
        ('Other', 'Other Service'),
        ('Parking', 'Car Parking'),
        ('Pool', 'Swimming Pool'),
        ('RoomService', 'Room Service'),
        ('Sauna', 'Sauna Session'),
        ('Spa', 'Spa Treatment'),
        ('WiFi', 'High-Speed Wi-Fi'),
    ]


    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Active', 'Active'),
        ('Completed', 'Completed'),
    ]

    client_name = models.CharField(max_length=200)
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES)
    description = models.TextField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.client_name} - {self.get_service_type_display()}"

    @property
    def duration(self):
        """Calculate duration in hours"""
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            return round(delta.total_seconds() / 3600, 2)  # Return hours
        return 0

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-start_time']
        verbose_name = 'Additional Service Package'
        verbose_name_plural = 'Additional Service Packages'