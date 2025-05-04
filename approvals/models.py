from django.db import models
from accounts.models import User
from bookings.models import Booking


class ApprovalStep(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField()
    required_role = models.CharField(max_length=50)

    class Meta:
        db_table = 'approval_step'
        ordering = ['order']

    def __str__(self):
        return self.name


class BookingApproval(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='approvals')
    step = models.ForeignKey(ApprovalStep, on_delete=models.CASCADE)
    approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='approvals')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'booking_approval'
        unique_together = ['booking', 'step']