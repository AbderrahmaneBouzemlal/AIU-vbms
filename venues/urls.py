""""""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import VenueViewSet

router = DefaultRouter()
router.register(r'venues', VenueViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

# Venues
"""
GET    /api/venues/                         # List all venues (with filters)
POST   /api/venues/                         # Create venue (staff)
GET    /api/venues/{id}/                    # Get venue details
PUT    /api/venues/{id}/                    # Update venue (staff)
DELETE /api/venues/{id}/                    # Delete venue (staff)
GET    /api/venues/{id}/availability/       # Get venue availability slots
POST   /api/venues/{id}/availability/       # Create availability slots (staff)
DELETE /api/venues/{id}/availability/{date}/ # Delete availability for date (staff)
"""
# Venue Search
"""
GET    /api/venues/search/                  # Search venues with multiple filters
GET    /api/venues/available/               # Get available venues for date/time range
"""