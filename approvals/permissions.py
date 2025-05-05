from rest_framework import permissions


class IsStaffOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and (request.user.is_staff or request.user.is_superuser)


class CanApproveBookings(permissions.BasePermission):
    def has_permission(self, request, view):
        if not (request.user and (request.user.is_staff or request.user.is_superuser)):
            return False

        # has_approval_perm = request.user.has_perm('bookings.can_approve_bookings')

        # if request.user.is_superuser or has_approval_perm:
        #     return True

        if request.user.user_type == 'staff':
            from accounts.models import StaffProfile
            staff_profile = StaffProfile.objects.get(user=request.user)
            booking_id = view.kwargs.get('booking_id')
            if booking_id:
                try:
                    from bookings.models import Booking
                    booking = Booking.objects.get(id=booking_id)
                    return booking.venue.handled_by == staff_profile.department
                except Exception as e:
                    pass

        return False