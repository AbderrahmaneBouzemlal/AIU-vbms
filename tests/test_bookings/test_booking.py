import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
import datetime
import json
from unittest.mock import patch

from venues.models import Venue
from accounts.models import User
from bookings.models import (
    Booking,
    EventDetail,
    BookingFile,
    BookingFeedback,
    BookingHistory,
    BookingStatus,
    DocumentType
)


@pytest.mark.django_db
class TestBookingListCreate:
    def test_list_bookings_unauthenticated(self, api_client):
        url = reverse('booking-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_bookings_user(self, authenticated_client, booking):
        url = reverse('booking-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == booking.id

    def test_list_bookings_admin(self, admin_client, booking):
        url = reverse('booking-list')
        response = admin_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_create_booking_unauthenticated(self, api_client, booking_data):
        url = reverse('booking-list')
        response = api_client.post(url, booking_data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_booking_authenticated(self, authenticated_client, booking_data):
        url = reverse('booking-list')
        response = authenticated_client.post(url, booking_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Booking.objects.count() == 1
        assert response.data['title'] == booking_data['title']

    def test_create_booking_with_event_details(self, authenticated_client, booking_data, event_detail_data):
        url = reverse('booking-list')
        data = booking_data.copy()
        data['event_detail'] = event_detail_data
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Booking.objects.count() == 1
        assert EventDetail.objects.count() == 1


@pytest.mark.django_db
class TestBookingDetailUpdateDelete:
    def test_get_booking_detail_unauthenticated(self, api_client, booking):
        url = reverse('booking-detail', kwargs={'pk': booking.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_booking_detail_owner(self, authenticated_client, booking):
        url = reverse('booking-detail', kwargs={'pk': booking.id})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == booking.id
        assert response.data['title'] == booking.title

    def test_get_booking_detail_admin(self, admin_client, booking):
        url = reverse('booking-detail', kwargs={'pk': booking.id})
        response = admin_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == booking.id

    def test_get_booking_detail_other_user(self, api_client, booking):
        other_user = User.objects.create_user(
            email='other@example.com',
            password='otherpassword123',
            user_type='student'

        )
        api_client.force_authenticate(user=other_user)

        url = reverse('booking-detail', kwargs={'pk': booking.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_booking_owner_pending(self, authenticated_client, booking):
        url = reverse('booking-detail', kwargs={'pk': booking.id})
        data = {
            'title': 'Updated Title',
            'description': 'Updated description'
        }
        response = authenticated_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Updated Title'
        booking.refresh_from_db()
        assert booking.title == 'Updated Title'

    def test_update_booking_owner_approved(self, authenticated_client, approved_booking):
        url = reverse('booking-detail', kwargs={'pk': approved_booking.id})
        data = {
            'title': 'Updated Title',
            'description': 'Updated description'
        }
        response = authenticated_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_booking_admin(self, admin_client, booking):
        url = reverse('booking-detail', kwargs={'pk': booking.id})
        data = {
            'title': 'Admin Updated Title',
            'description': 'Admin updated description'
        }
        response = admin_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        booking.refresh_from_db()
        assert booking.title == 'Admin Updated Title'

    def test_delete_booking(self, authenticated_client, booking):
        url = reverse('booking-detail', kwargs={'pk': booking.id})
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        booking.refresh_from_db()
        assert booking.status == BookingStatus.CANCELLED


@pytest.mark.django_db
class TestBookingStatusUpdate:
    def test_update_status_unauthenticated(self, api_client, booking):
        url = reverse('booking-update-status', kwargs={'pk': booking.id})
        data = {'status': BookingStatus.APPROVED}
        response = api_client.put(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_status_owner(self, authenticated_client, booking):
        url = reverse('booking-update-status', kwargs={'pk': booking.id})
        data = {'status': BookingStatus.APPROVED}
        response = authenticated_client.put(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_status_admin(self, admin_client, booking):
        url = reverse('booking-update-status', kwargs={'pk': booking.id})
        data = {
            'status': BookingStatus.APPROVED,
            'comment': 'Approved by admin',
            'handled_by_role': 'admin'
        }
        response = admin_client.put(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        booking.refresh_from_db()
        assert booking.status == BookingStatus.APPROVED

        assert BookingHistory.objects.filter(booking=booking).exists()
        history = BookingHistory.objects.get(booking=booking)
        assert history.previous_status == BookingStatus.PENDING
        assert history.new_status == BookingStatus.APPROVED
        assert history.comment == 'Approved by admin'

    def test_update_status_with_feedback(self, admin_client, booking):
        url = reverse('booking-update-status', kwargs={'pk': booking.id})
        data = {
            'status': BookingStatus.APPROVED,
            'comment': 'Approved with feedback',
            'feedback': 'This is admin feedback',
            'feedback_is_internal': False,
            'feedback_type': 'approval'
        }
        response = admin_client.put(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK

        assert BookingFeedback.objects.filter(booking=booking).exists()
        feedback = BookingFeedback.objects.get(booking=booking)
        assert feedback.content == 'This is admin feedback'
        assert feedback.is_internal == False
        assert feedback.feedback_type == 'approval'


@pytest.mark.django_db
class TestBookingHistoryFeedback:
    def test_get_history_unauthenticated(self, api_client, booking):
        url = reverse('booking-history', kwargs={'pk': booking.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_history_owner(self, authenticated_client, booking):
        url = reverse('booking-history', kwargs={'pk': booking.id})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_history_admin(self, admin_client, booking):
        # Create history entry
        BookingHistory.objects.create(
            booking=booking,
            previous_status=BookingStatus.PENDING,
            new_status=BookingStatus.APPROVED,
            changed_by=admin_client.handler._force_user,
            comment='Test history entry'
        )

        url = reverse('booking-history', kwargs={'pk': booking.id})
        response = admin_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['comment'] == 'Test history entry'

    def test_add_feedback_unauthenticated(self, api_client, booking):
        url = reverse('booking-add-feedback', kwargs={'pk': booking.id})
        data = {'content': 'Test feedback', 'is_internal': False}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_add_feedback_owner(self, authenticated_client, booking):
        url = reverse('booking-add-feedback', kwargs={'pk': booking.id})
        data = {'content': 'Test feedback', 'is_internal': False}
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_add_feedback_admin(self, admin_client, booking):
        url = reverse('booking-add-feedback', kwargs={'pk': booking.id})
        data = {
            'content': 'Test admin feedback',
            'is_internal': True,
            'feedback_type': 'general'
        }
        response = admin_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert BookingFeedback.objects.filter(booking=booking).exists()
        feedback = BookingFeedback.objects.get(booking=booking)
        assert feedback.content == 'Test admin feedback'
        assert feedback.is_internal == True


@pytest.mark.django_db
class TestEventDetails:
    def test_get_event_details_not_found(self, authenticated_client, booking):
        url = reverse('booking-event-detail-detail', kwargs={'booking_pk': booking.id, 'pk': 1237890})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_event_details(self, authenticated_client, booking, event_detail):
        url = reverse('booking-event-detail-detail', kwargs={'booking_pk': booking.id, 'pk': event_detail.id})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['event_type'] == event_detail.event_type

    def test_create_event_details(self, authenticated_client, booking, event_detail_data):
        url = reverse('booking-event-detail-list', kwargs={'booking_pk': booking.id})
        response = authenticated_client.post(url, event_detail_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert EventDetail.objects.filter(booking=booking).exists()

    def test_create_event_details_already_exists(self, authenticated_client, booking, event_detail):
        url = reverse('booking-event-detail-list', kwargs={'booking_pk': booking.id})
        data = {
            'event_type': 'party',
            'purpose': 'Testing purposes'
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_event_details(self, authenticated_client, booking, event_detail):
        url = reverse('booking-event-detail-detail', kwargs={'booking_pk': booking.id, 'pk': event_detail.id})
        data = {'event_type': 'party', 'purpose': 'Updated purpose'}
        response = authenticated_client.put(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        event_detail.refresh_from_db()
        assert event_detail.event_type == 'party'
        assert event_detail.purpose == 'Updated purpose'


@pytest.mark.django_db
class TestBookingFiles:
    def test_get_files_list(self, authenticated_client, booking, booking_file):
        url = reverse('booking-file-list', kwargs={'booking_pk': booking.id})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['file_name'] == 'test_file.pdf'

    def test_download_file(self, authenticated_client, booking, booking_file):
        url = reverse('booking-file-download-file', kwargs={'booking_pk': booking.id, 'pk': booking_file.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        assert 'attachment' in response['Content-Disposition']
        assert f'filename="{booking_file.file_name}"' in response['Content-Disposition']

    def test_upload_file(self, authenticated_client, booking):
        url = reverse('booking-file-list', kwargs={'booking_pk': booking.id})
        file_content = b'new test file content'
        test_file = SimpleUploadedFile(
            name='new_test_file.pdf',
            content=file_content,
            content_type='application/pdf'
        )

        data = {
            'file': test_file,
            'file_name': 'new_test_file.pdf',
            'file_type': 'application/pdf',
            'document_type': DocumentType.DEAN_APPROVAL,
            'description': 'New test file description'
        }

        response = authenticated_client.post(url, data, format='multipart')
        assert response.status_code == status.HTTP_201_CREATED
        assert BookingFile.objects.filter(booking=booking, file_name='new_test_file.pdf').exists()

    def test_verify_file_owner(self, authenticated_client, booking, booking_file):
        url = reverse('booking-file-verify-file', kwargs={
            'booking_pk': booking.id,
            'pk': booking_file.id
        })
        response = authenticated_client.post(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_verify_file_admin(self, admin_client, booking, booking_file):
        url = reverse('booking-file-verify-file', kwargs={
            'booking_pk': booking.id,
            'pk': booking_file.id
        })
        response = admin_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        booking_file.refresh_from_db()
        assert booking_file.is_verified == True
        assert booking_file.verified_by == admin_client.handler._force_user

    def test_delete_file(self, authenticated_client, booking, booking_file):
        url = reverse('booking-file-detail', kwargs={
            'booking_pk': booking.id,
            'pk': booking_file.id
        })
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not BookingFile.objects.filter(id=booking_file.id).exists()


@pytest.mark.django_db
class TestCalendarViews:
    def test_calendar_unauthenticated(self, api_client):
        url = reverse('calendar-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_calendar_user(self, authenticated_client, booking, approved_booking):
        other_user = User.objects.create_user(
            email='other@example.com',
            password='otherpassword123',
            user_type='student'
        )
        approved_booking.user = other_user
        approved_booking.save()

        url = reverse('calendar-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_calendar_admin(self, admin_client, booking, approved_booking):
        url = reverse('calendar-list')
        response = admin_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_venue_calendar(self, authenticated_client, booking, approved_booking):
        other_venue = Venue.objects.create(
            name='Other Venue',
            location='Other Location',
            category='category',
            capacity=200
        )
        approved_booking.venue = other_venue
        approved_booking.save()

        url = reverse('calendar-venue-calendar', kwargs={'venue_id': other_venue.id})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['venue_name'] == other_venue.name

    def test_user_calendar(self, authenticated_client, booking, approved_booking):
        other_user = User.objects.create_user(
            email='other@example.com',
            password='otherpassword123',
            user_type='student'
        )
        approved_booking.user = other_user
        approved_booking.save()

        url = reverse('calendar-user-calendar')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == booking.id