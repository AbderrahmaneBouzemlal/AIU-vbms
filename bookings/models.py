from django.db import models
from accounts.models import User
from venues.models import Venue


class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('canceled', 'Canceled'),
        ('completed', 'Completed'),
    )

    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='bookings')
    event_title = models.CharField(max_length=200)
    event_description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    attendees_count = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'booking'

    def __str__(self):
        return f"{self.event_title} - {self.venue.name}"


class BookingAttachment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='booking_attachments/')
    file_name = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'booking_attachment'


class BookingRequirement(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='requirements')
    requirement_type = models.CharField(max_length=100)  # e.g., "technical", "furniture", "catering"
    description = models.TextField()
    status = models.CharField(max_length=20, default='pending')

    class Meta:
        db_table = 'booking_requirement'