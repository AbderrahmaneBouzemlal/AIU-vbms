from rest_framework import permissions
from .models import Booking, BookingStatus


class CanManageBooking(permissions.BasePermission):
    """
    Permission to check if user can manage a booking:
    - Owner can manage if booking is in pending or approved status
    - Staff/admin can manage regardless of status
    """

    def has_permission(self, request, view):
        # Get the booking
        booking_pk = view.kwargs.get('booking_pk')
        if not booking_pk:
            return False

        try:
            booking = Booking.objects.get(pk=booking_pk)
        except Booking.DoesNotExist:
            return False

        # Check if user is staff/admin
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Check if user is the owner
        if booking.user != request.user:
            return False

        # Owner can only manage in certain statuses
        if booking.status in [BookingStatus.PENDING, BookingStatus.APPROVED]:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        # Get the booking
        if isinstance(obj, Booking):
            booking = obj
        elif hasattr(obj, 'booking'):
            booking = obj.booking
        else:
            return False

        # Check if user is staff/admin
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Check if user is the owner
        if booking.user != request.user:
            return False

        # Owner can only manage in certain statuses
        if booking.status in [BookingStatus.PENDING, BookingStatus.APPROVED]:
            return True

        return False