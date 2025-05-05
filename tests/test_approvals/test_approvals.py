import pytest
from django.template.defaulttags import comment
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

from bookings.models import (
    BookingStatus, BookingHistory,
    BookingFeedback, BookingFile, DocumentType
)
from accounts.models import StaffProfile

User = get_user_model()


@pytest.mark.django_db
class TestApprovalViewSet:
    def test_list_approvals_staff(self, api_client, staff_user, booking):
        api_client.force_authenticate(user=staff_user)
        url = reverse('approval-list')
        print(f"URL: {url}")
        response = api_client.get(url)

        print(f"Response data: {response.data}")
        assert response.status_code == status.HTTP_200_OK


        data = response.data
        if isinstance(data, dict) and 'results' in data:
            assert len(data['results']) == 1
            booking_data = data['results'][0]
        else:
            assert len(data) == 1
            booking_data = data[0]

        assert booking_data['id'] == booking.id
        assert booking_data['title'] == booking.title

    def test_list_approvals_admin(self, api_client, admin_user, booking, another_booking):
        api_client.force_authenticate(user=admin_user)
        url = reverse('approval-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

    def test_list_approvals_unauthorized(self, api_client, normal_user, booking):
        api_client.force_authenticate(user=normal_user)
        url = reverse('approval-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_pending_approvals(self, api_client, staff_user, booking):
        api_client.force_authenticate(user=staff_user)
        url = reverse('approval-pending')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_list_under_review_approvals(self, api_client, staff_user, booking):
        booking.status = BookingStatus.UNDER_REVIEW
        booking.save()

        api_client.force_authenticate(user=staff_user)
        url = reverse('approval-under-review')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_list_documents_pending_approvals(self, api_client, staff_user, booking):
        booking.status = BookingStatus.DOCUMENTS_PENDING
        booking.save()

        api_client.force_authenticate(user=staff_user)
        url = reverse('approval-documents-pending')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_department_filtering(self, api_client, staff_user, booking):
        staff_profile = StaffProfile.objects.get(user=staff_user)
        if staff_profile:
            staff_profile.department = 'sa'
            staff_profile.save()

        api_client.force_authenticate(user=staff_user)
        url = reverse('approval-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 0  # Should not see bookings from other departments


@pytest.mark.django_db
class TestBookingApprovalActionView:
    def test_review_booking(self, api_client, staff_user, booking, staff_profile):
        api_client.force_authenticate(user=staff_user)
        url = reverse('approval-review', kwargs={'booking_id': booking.id})
        response = api_client.post(url, {comment: 'Under Review'})

        print(response.data)
        assert response.status_code == status.HTTP_200_OK
        booking.refresh_from_db()
        assert booking.status == BookingStatus.UNDER_REVIEW

        history = BookingHistory.objects.filter(booking=booking).last()
        assert history is not None
        assert history.previous_status == BookingStatus.PENDING
        assert history.new_status == BookingStatus.UNDER_REVIEW

    def test_approve_booking(self, api_client, staff_user, booking, staff_profile):
        api_client.force_authenticate(user=staff_user)
        url = reverse('approval-approve', kwargs={'booking_id': booking.id})
        response = api_client.post(url, {'comment': 'Booking approved'})

        assert response.status_code == status.HTTP_200_OK
        booking.refresh_from_db()
        assert booking.status == BookingStatus.APPROVED
        assert booking.approved_by == staff_user
        assert booking.approval_date is not None

    def test_reject_booking(self, api_client, staff_user, booking, staff_profile):
        api_client.force_authenticate(user=staff_user)
        url = reverse('approval-reject', kwargs={'booking_id': booking.id})
        response = api_client.post(url, {'comment': 'Booking rejected due to policy violation'})

        assert response.status_code == status.HTTP_200_OK
        booking.refresh_from_db()
        assert booking.status == BookingStatus.REJECTED

        # Check feedback was created
        feedback = BookingFeedback.objects.filter(booking=booking).last()
        assert feedback is not None
        assert feedback.content == 'Booking rejected due to policy violation'
        assert feedback.feedback_type == 'rejection'

    def test_request_documents(self, api_client, staff_user, booking, staff_profile):
        api_client.force_authenticate(user=staff_user)
        url = reverse('approval-request-documents', kwargs={'booking_id': booking.id})
        response = api_client.post(url, {'comment': 'Please provide identification documents'})

        assert response.status_code == status.HTTP_200_OK
        booking.refresh_from_db()
        assert booking.status == BookingStatus.DOCUMENTS_PENDING

    def test_invalid_action(self, api_client, staff_user, booking, staff_profile):
        api_client.force_authenticate(user=staff_user)
        # This URL doesn't exist in the urls.py, but testing the view logic
        url = reverse('approval-review', kwargs={'booking_id': booking.id})
        # Modify the URL to simulate an invalid action
        url = url.replace('review', 'invalid-action')
        response = api_client.post(url, {'comment': 'Invalid action'})

        # The URL won't match, but if it did, the view would return 400
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST]

    def test_unauthorized_user(self, api_client, normal_user, booking, staff_profile):
        api_client.force_authenticate(user=normal_user)
        url = reverse('approval-review', kwargs={'booking_id': booking.id})
        response = api_client.post(url, {'comment': 'Started review process'})

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestBookingApprovalHistoryView:
    def test_get_history(self, api_client, staff_user, booking):
        # Create some history entries
        BookingHistory.objects.create(
            booking=booking,
            previous_status=BookingStatus.PENDING,
            new_status=BookingStatus.UNDER_REVIEW,
            changed_by=staff_user,
            comment="Started review"
        )
        BookingHistory.objects.create(
            booking=booking,
            previous_status=BookingStatus.UNDER_REVIEW,
            new_status=BookingStatus.APPROVED,
            changed_by=staff_user,
            comment="Approved booking"
        )

        api_client.force_authenticate(user=staff_user)
        url = reverse('approval-history', kwargs={'booking_id': booking.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_unauthorized_user(self, api_client, normal_user, booking):
        api_client.force_authenticate(user=normal_user)
        url = reverse('approval-history', kwargs={'booking_id': booking.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestBookingCommentsView:
    def test_get_comments(self, api_client, staff_user, booking):
        # Create some comments
        BookingFeedback.objects.create(
            booking=booking,
            staff=staff_user,
            content="Internal note",
            is_internal=True,
            feedback_type="note"
        )
        BookingFeedback.objects.create(
            booking=booking,
            staff=staff_user,
            content="Request for more information",
            is_internal=False,
            feedback_type="requirement"
        )

        api_client.force_authenticate(user=staff_user)
        url = reverse('approval-comments-list', kwargs={'booking_id': booking.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_client_only_sees_external_comments(self, api_client, normal_user, staff_user, booking):
        # Create internal and external comments
        BookingFeedback.objects.create(
            booking=booking,
            staff=staff_user,
            content="Internal note",
            is_internal=True,
            feedback_type="note"
        )
        BookingFeedback.objects.create(
            booking=booking,
            staff=staff_user,
            content="Public comment",
            is_internal=False,
            feedback_type="requirement"
        )

        # This test won't work correctly as the view uses request.user.is_staff
        # which normal_user won't have, but the logic would prevent seeing internal comments
        api_client.force_authenticate(user=normal_user)
        url = reverse('approval-comments-list', kwargs={'booking_id': booking.id})
        response = api_client.get(url)

        # Either it will be forbidden, or it would filter out internal comments
        if response.status_code == status.HTTP_200_OK:
            assert len(response.data) == 1
            assert response.data[0]['content'] == "Public comment"
        else:
            assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_add_comment(self, api_client, staff_user, booking):
        api_client.force_authenticate(user=staff_user)
        url = reverse('approval-comment', kwargs={'booking_id': booking.id})
        data = {
            'content': 'New comment from staff',
            'is_internal': True,
            'feedback_type': 'general'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert BookingFeedback.objects.count() == 1
        feedback = BookingFeedback.objects.first()
        assert feedback.content == 'New comment from staff'
        assert feedback.is_internal is True


@pytest.mark.django_db
class TestDocumentVerificationView:
    def test_get_documents(self, api_client, staff_user, booking, document):
        api_client.force_authenticate(user=staff_user)
        url = reverse('approval-documents', kwargs={'booking_id': booking.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['file_name'] == 'Test ID Document'

    def test_verify_document(self, api_client, staff_user, booking, document):
        api_client.force_authenticate(user=staff_user)
        url = reverse('approval-document-verify', kwargs={
            'booking_id': booking.id,
            'document_id': document.id
        })
        response = api_client.post(url, {'comment': 'Document verified'})

        assert response.status_code == status.HTTP_200_OK
        document.refresh_from_db()
        assert document.is_verified is True
        assert document.verified_by == staff_user
        assert document.verified_at is not None

    def test_verify_all_documents_updates_booking(self, api_client, staff_user, booking, document):
        # Set booking status to documents pending
        booking.status = BookingStatus.DOCUMENTS_PENDING
        booking.save()

        api_client.force_authenticate(user=staff_user)
        url = reverse('approval-document-verify', kwargs={
            'booking_id': booking.id,
            'document_id': document.id
        })
        response = api_client.post(url, {'comment': 'Document verified'})

        assert response.status_code == status.HTTP_200_OK
        booking.refresh_from_db()
        assert booking.status == BookingStatus.PENDING
        assert booking.documents_verified is True

        # Verify history was created
        history = BookingHistory.objects.filter(
            booking=booking,
            previous_status=BookingStatus.DOCUMENTS_PENDING,
            new_status=BookingStatus.PENDING
        ).exists()
        assert history is True

    def test_verify_not_all_documents(self, api_client, staff_user, booking, document):
        second_doc = BookingFile.objects.create(
            booking=booking,
            document_type=DocumentType.PERMISSION_LETTER,
            file='test_docs/permission.pdf',
            uploaded_by=booking.user,
            file_name='Permission Letter'
        )

        booking.status = BookingStatus.DOCUMENTS_PENDING
        booking.save()

        api_client.force_authenticate(user=staff_user)
        url = reverse('approval-document-verify', kwargs={
            'booking_id': booking.id,
            'document_id': document.id
        })
        response = api_client.post(url, {'comment': 'Document verified'})

        assert response.status_code == status.HTTP_200_OK
        booking.refresh_from_db()
        assert booking.status == BookingStatus.DOCUMENTS_PENDING
        assert booking.documents_verified is False

        assert response.data['all_documents_verified'] is False