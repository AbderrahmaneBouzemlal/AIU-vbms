from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone
from venues.models import Venue

User = get_user_model()


class BookingStatus(models.TextChoices):
    PENDING = 'pending', _('Pending')
    UNDER_REVIEW = 'under_review', _('Under Review')
    APPROVED = 'approved', _('Approved')
    REJECTED = 'rejected', _('Rejected')
    CANCELLED = 'cancelled', _('Cancelled')
    COMPLETED = 'completed', _('Completed')
    PAYMENT_PENDING = 'payment_pending', _('Payment Pending')
    DOCUMENTS_PENDING = 'documents_pending', _('Documents Pending')


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='bookings')

    booking_code = models.CharField(max_length=20, unique=True, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    attendees_count = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    payment_required = models.BooleanField(default=False)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_completed = models.BooleanField(default=False)
    payment_reference = models.CharField(max_length=100, blank=True)

    requires_approval = models.BooleanField(default=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='approved_bookings')
    approval_date = models.DateTimeField(null=True, blank=True)

    documents_required = models.BooleanField(default=False)
    documents_verified = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['user']),
            models.Index(fields=['venue']),
            models.Index(fields=['start_time', 'end_time']),
        ]
        db_table = 'booking'

    def __str__(self):
        return f"{self.title} ({self.venue.name})"

    @property
    def is_past(self):
        from django.utils import timezone
        return self.end_time < timezone.now()

    @property
    def duration_hours(self):
        delta = self.end_time - self.start_time
        return delta.total_seconds() / 3600

    def save(self, *args, **kwargs):
        if not self.booking_code:
            now = timezone.now()
            year = now.year
            month = now.month
            count = Booking.objects.filter(
                created_at__year=year,
                created_at__month=month
            ).count() + 1
            self.booking_code = f"BK-{year}{month:02d}-{count:04d}"

        if not self.pk:
            handled_by = self.venue.handled_by
            self.payment_required = handled_by == 'ppk'
            self.documents_required = handled_by == 'sa' or handled_by == 'ppk'
            self.requires_approval = handled_by == 'sa'

        super().save(*args, **kwargs)


class EventDetail(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='event_detail')
    event_type = models.CharField(max_length=100)
    purpose = models.TextField()
    equipment_needed = models.TextField(blank=True)
    special_requests = models.TextField(blank=True)
    setup_time = models.DateTimeField(null=True, blank=True)
    teardown_time = models.DateTimeField(null=True, blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    organizer_name = models.CharField(max_length=255, blank=True)
    organizer_contact = models.CharField(max_length=100, blank=True)
    event_schedule = models.TextField(blank=True, help_text="Detailed schedule of the event")

    class Meta:
        db_table = 'booking_event_detail'
        verbose_name = 'Event Detail'
        verbose_name_plural = 'Event Details'

    def __str__(self):
        return f"Details for {self.booking.title}"


class DocumentType(models.TextChoices):
    DEAN_APPROVAL = 'dean_approval', _('Dean Approval')
    BUDGET_PLAN = 'budget_plan', _('Budget Plan')
    EVENT_SCHEDULE = 'event_schedule', _('Event Schedule')
    PAYMENT_PROOF = 'payment_proof', _('Payment Proof')
    PERMISSION_LETTER = 'permission_letter', _('Permission Letter')
    VENUE_SETUP = 'venue_setup', _('Venue Setup Plan')
    OTHER = 'other', _('Other Document')


class BookingFile(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='files')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_files')
    file = models.FileField(upload_to='booking_files/%Y/%m/%d/')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)
    document_type = models.CharField(
        max_length=100,
        choices=DocumentType.choices,
        default=DocumentType.OTHER,
        help_text="Type of document being uploaded"
    )
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='verified_files')
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.file_name} ({self.document_type})"

    def save(self, *args, **kwargs):
        if self.uploaded_by is None:
            booking = Booking.objects.filter(id=self.booking)
            self.uploaded_by = booking.user.first()
        super().save(*args, **kwargs)
    class Meta:
        ordering = ['-uploaded_at']
        db_table = 'booking_file'
        verbose_name = 'Booking File'
        verbose_name_plural = 'Booking Files'


class BookingHistory(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='history')
    previous_status = models.CharField(max_length=20, choices=BookingStatus.choices)
    new_status = models.CharField(max_length=20, choices=BookingStatus.choices)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='booking_status_changes')
    timestamp = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)
    handled_by_role = models.CharField(max_length=50, blank=True, help_text="Role of the person who made this change")

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Booking histories'
        db_table = 'booking_history'
        verbose_name = 'Booking History'
        verbose_name_plural = 'Booking Histories'

    def __str__(self):
        return f"Status change: {self.previous_status} → {self.new_status}"


class BookingFeedback(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='feedback')
    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='provided_feedback')
    content = models.TextField()
    is_internal = models.BooleanField(default=True, help_text="If True, only visible to staff")
    feedback_type = models.CharField(max_length=50, default='general',
                                     choices=[('general', 'General Feedback'),
                                              ('rejection', 'Rejection Reason'),
                                              ('approval', 'Approval Notes'),
                                              ('requirement', 'Additional Requirements')])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'booking_feedback'
        verbose_name = 'Booking Feedback'
        verbose_name_plural = 'Booking Feedback'

    def __str__(self):
        return f"Feedback on {self.booking.title}"
