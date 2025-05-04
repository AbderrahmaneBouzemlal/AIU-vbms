from venv import create

import pytest
import datetime
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from accounts.models import User
from venues.models import Venue, VenueCategory
from bookings.models import Booking, BookingStatus, EventDetail, BookingFile, DocumentType
from accounts.serializers import StaffProfileSerializer, AdminProfileSerializer, StudentProfileSerializer
from accounts.models import AdminProfile, StaffProfile, StudentProfile


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_data():
    return {
        'email': 'user@example.com',
        'password': 'testpassword123',
        'first_name': 'Test',
        'last_name': 'User',
        'user_type': 'student'
    }


@pytest.fixture
def admin_data():
    return {
        'email': 'admin@example.com',
        'password': 'adminpassword123',
        'first_name': 'Admin',
        'last_name': 'User',
        'user_type': 'admin'
    }

@pytest.fixture
def venue_category_data():
    return {
        'name': 'Football Field',
        'description': 'The football field is a great place to play football. It has a lot of stadiums and many different types of football fields. It is also known as the best stadium in the world. ',
    }

@pytest.fixture
def venue_category(venue_category_data):
    return VenueCategory.objects.create(**venue_category_data)

@pytest.fixture
def other_category(venue_category_data):
    venue_category_data.update({'name': 'Concert Hall', 'description': 'A concert hall for concerts and events'})
    return VenueCategory.objects.create(**venue_category_data)

@pytest.fixture
def venue_data(venue_category):
    return {
        'name': 'Test Venue',
        'location': 'Test Location',
        'capacity': 100,
        'description': 'A test venue for testing',
        'requires_payment': True,
        'is_available': True,
        'category': venue_category,
    }

@pytest.fixture
def booking_data(venue):
    start_time = timezone.now() + datetime.timedelta(days=1)
    end_time = start_time + datetime.timedelta(hours=2)
    return {
        'title': 'Test Booking',
        'description': 'A test booking for testing',
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'venue_id': venue.id,
        'attendees_count': 50
    }


@pytest.fixture
def event_detail_data():
    return {
        'event_type': 'conference',
        'purpose': 'Testing purposes',
        'equipment_needed': 'Projector, Microphone',
        'special_requests': 'None',
        'setup_time': '2024-12-23 01:00:00',
        'teardown_time': '2024-12-23 02:00:00',
        'budget': 500.00,
        'organizer_name': 'Test Organizer',
        'organizer_contact': 'organizer@example.com',
        'event_schedule': 'Test schedule'
    }


@pytest.fixture
def user(user_data):
    return User.objects.create_user(**user_data)

#
# @pytest.fixture
# def create_user(db, django_user_model):
#     def _create_user(email="test@example.com", password="testpass123",
#                      user_type="student", profile_data=None, **kwargs):
#         user = django_user_model.objects.create_user(
#             email=email,
#             password=password,
#             user_type=user_type,
#             **kwargs
#         )
#         if profile_data:
#             if user.user_type == 'admin':
#                 profile = AdminProfile.objects.get(user=user)
#                 serializer = AdminProfileSerializer(profile, data=profile_data, partial=True)
#             elif user.user_type == 'staff':
#                 profile = StaffProfile.objects.get(user=user)
#                 serializer = StaffProfileSerializer(profile, data=profile_data, partial=True)
#             else:
#                 profile = StudentProfile.objects.get(user=user)
#                 serializer = StudentProfileSerializer(profile, data=profile_data, partial=True)
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#
#         return user
#
#     return _create_user

@pytest.fixture
def admin_user(admin_data):
    return User.objects.create_superuser(**admin_data)

@pytest.fixture
def venue(venue_data):
    return Venue.objects.create(**venue_data)

@pytest.fixture
def another_venue(venue_data, other_category):
    venue_data.update({
        'name': 'Convocation Hall',
        'description': 'Is an area that you can rent for multiple events',
        'handled_by': 'ppk',
        'capacity': 1000,
        'location': 'In the university',
        'category': other_category,
        'requires_payment': True,
        'requires_documents': True
    })
    return Venue.objects.create(**venue_data)

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def booking(user, venue):
    start_time = timezone.now() + datetime.timedelta(days=1)
    end_time = start_time + datetime.timedelta(hours=2)
    booking = Booking.objects.create(
        user=user,
        venue=venue,
        title='Test Booking',
        description='A test booking for testing',
        start_time=start_time,
        end_time=end_time,
        attendees_count=50,
        status=BookingStatus.PENDING
    )
    return booking

@pytest.fixture
def approved_booking(user, venue, admin_user):
    start_time = timezone.now() + datetime.timedelta(days=1)
    end_time = start_time + datetime.timedelta(hours=2)
    booking = Booking.objects.create(
        user=user,
        venue=venue,
        title='Approved Booking',
        description='An approved booking for testing',
        start_time=start_time,
        end_time=end_time,
        attendees_count=50,
        status=BookingStatus.APPROVED,
        approved_by=admin_user,
        approval_date=timezone.now()
    )
    return booking



@pytest.fixture
def event_detail(booking, event_detail_data):
    return EventDetail.objects.create(booking=booking, **event_detail_data)


@pytest.fixture
def booking_file(booking, user):
    file_content = b'test file content'
    test_file = SimpleUploadedFile(
        name='test_file.pdf',
        content=file_content,
        content_type='application/pdf'
    )

    return BookingFile.objects.create(
        booking=booking,
        file=test_file,
        file_name='test_file.pdf',
        file_type='application/pdf',
        document_type=DocumentType.DEAN_APPROVAL,
        description='Test file description',
        uploaded_by=user
    )
