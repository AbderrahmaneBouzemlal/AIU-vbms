# from django.db.models.signals import post_save, pre_save
# from django.dispatch import receiver
# from .models import Booking, BookingHistory, BookingStatus
#
#
# @receiver(pre_save, sender=Booking)
# def track_booking_status_change(sender, instance, **kwargs):
#     """Track changes to booking status and create history entries"""
#     if instance.pk:  # Only for existing bookings
#         try:
#             old_instance = Booking.objects.get(pk=instance.pk)
#             if old_instance.status != instance.status:
#                 # Create history entry after the save completes
#                 # We'll use post_save signal to ensure the booking is saved first
#                 instance._old_status = old_instance.status
#                 instance._status_changed = True
#             else:
#                 instance._status_changed = False
#         except Booking.DoesNotExist:
#             pass  # New instance, nothing to track
#
#
# @receiver(post_save, sender=Booking)
# def create_booking_history(sender, instance, created, **kwargs):
#     """Create history entry after status change is saved"""
#     if not created and hasattr(instance, '_status_changed') and instance._status_changed:
#         BookingHistory.objects.create(
#             booking=instance,
#             previous_status=instance._old_status,
#             new_status=instance.status,
#             # If available in the request context, we'd get the user from there
#             changed_by=instance.approved_by if instance.status == BookingStatus.APPROVED else None,
#             comment=f"Status updated from {instance._old_status} to {instance.status}"
#         )
#
#     # When a booking is first created that requires documents, set status to DOCUMENTS_PENDING
#     if created and instance.documents_required and not instance.documents_verified:
#         if instance.status == BookingStatus.PENDING:
#             instance.status = BookingStatus.DOCUMENTS_PENDING
#             # Avoid recursive loop by using update instead of save
#             Booking.objects.filter(pk=instance.pk).update(status=BookingStatus.DOCUMENTS_PENDING)
#
#             # Create initial history entry
#             BookingHistory.objects.create(
#                 booking=instance,
#                 previous_status=BookingStatus.PENDING,
#                 new_status=BookingStatus.DOCUMENTS_PENDING,
#                 changed_by=None,
#                 comment="Automatic status update: Documents required"
#             )