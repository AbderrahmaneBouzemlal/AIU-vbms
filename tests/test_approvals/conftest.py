import pytest
from rest_framework.test import APIClient
from django.utils import timezone
import uuid
from bookings.models import (
    Booking, BookingStatus,
    BookingFile, DocumentType
)
from accounts.models import StaffProfile
from venues.models import Venue
from accounts.models import User


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def staff_user():
    user = User.objects.create_user(
        email='staff@example.com',
        password='staffpass123',
        first_name='staff',
        last_name='User',
        user_type='staff'
    )
    return user

@pytest.fixture
def staff_profile(staff_user):
    profile = StaffProfile.objects.get(
        user=staff_user,
    )
    profile.department = 'ppk'
    profile.save()

@pytest.fixture
def admin_user():
    return User.objects.create_user(
        email='admin@example.com',
        password='admi#$#$33npass123',
        first_name='Admin',
        last_name='User',
        user_type='admin'
    )

@pytest.fixture
def venue():
    return Venue.objects.create(
        name='Main Conference Room',
        category='Conference Room',
        handled_by='ppk',
        capacity=50
    )


@pytest.fixture
def normal_user():
    return User.objects.create_user(
        email='user@example.com',
        password='userpass123',
        first_name='Normal',
        last_name='User',
        user_type='student'
    )


@pytest.fixture
def booking(normal_user, venue):
    return Booking.objects.create(
        user=normal_user,
        venue=venue,
        title='Test Booking',
        description='Test booking description',
        booking_code=str(uuid.uuid4())[:8].upper(),
        start_time=timezone.now() + timezone.timedelta(days=5),
        end_time=timezone.now() + timezone.timedelta(days=5, hours=2),
        status=BookingStatus.PENDING,
        requires_approval=True,
        attendees_count=100
    )

@pytest.fixture
def another_booking(normal_user, venue):
    return Booking.objects.create(
        user=normal_user,
        venue=venue,
        title='request to join another booking',
        description='Test booking description',
        booking_code=str(uuid.uuid4())[:8].upper(),
        start_time=timezone.now() + timezone.timedelta(days=5),
        end_time=timezone.now() + timezone.timedelta(days=5, hours=2),
        status=BookingStatus.PENDING,
        requires_approval=True,
        attendees_count=100
    )

@pytest.fixture
def document(booking):
    return BookingFile.objects.create(
        booking=booking,
        document_type=DocumentType.DEAN_APPROVAL,
        file='test_docs/test.pdf',
        uploaded_by=booking.user,
        file_name='Test ID Document'
    )

