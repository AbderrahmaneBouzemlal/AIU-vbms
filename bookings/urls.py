""""""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import (
    BookingViewSet,
    EventDetailViewSet,
    BookingFileViewSet,
    CalendarViewSet
)

# Main router for bookings
router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'calendar', CalendarViewSet, basename='calendar')

# Nested router for event details
booking_router = routers.NestedSimpleRouter(router, r'bookings', lookup='booking')
booking_router.register(r'event-details', EventDetailViewSet, basename='booking-event-detail')
booking_router.register(r'files', BookingFileViewSet, basename='booking-file')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(booking_router.urls)),
]

"""
# Bookings
GET    /api/bookings/                       # List bookings (filtered by user role)
POST   /api/bookings/                       # Create new booking request
GET    /api/bookings/{id}/                  # Get booking details
PUT    /api/bookings/{id}/                  # Update booking (if still pending)
DELETE /api/bookings/{id}/                  # Cancel booking
PUT    /api/bookings/{id}/status/           # Update booking status (admin/staff)
POST   /api/bookings/{id}/feedback/   # Provide feedback on booking (staff)
GET    /api/bookings/{id}/history/    # View approval history (staff)

# Event Details
POST   /api/bookings/{id}/event-details/    # Add event details
PUT    /api/bookings/{id}/event-details/    # Update event details
GET    /api/bookings/{id}/event-details/    # Get event details

# File Uploads for Bookings
POST   /api/bookings/{id}/files/             # Upload files for a booking
GET    /api/bookings/{id}/files/             # Get uploaded files list
GET    /api/bookings/{id}/files/{file_id}/   # Download specific file
DELETE /api/bookings/{id}/files/{file_id}/   # Delete uploaded file

# Booking Calendar
GET    /api/calendar/                       # Get calendar events (bookings)
GET    /api/calendar/venue/{id}/            # Get calendar for specific venue
GET    /api/calendar/user/                  # Get current user's bookings calendar

"""