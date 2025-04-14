from django.db import models
from accounts.models import User


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('booking_status', 'Booking Status Update'),
        ('approval_request', 'Approval Request'),
        ('reminder', 'Reminder'),
        ('system', 'System Notification'),
    )

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    related_object_id = models.IntegerField(null=True, blank=True)  # ID of related object (booking, approval, etc.)
    related_object_type = models.CharField(max_length=50, blank=True, null=True)  # Type of related object
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notification'
        ordering = ['-created_at']


class EmailLog(models.Model):
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)  # success, failed

    class Meta:
        db_table = 'email_log'