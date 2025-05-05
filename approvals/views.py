from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Count, Avg, Q, F
from django.shortcuts import get_object_or_404

from bookings.models import (
    Booking, BookingStatus, BookingHistory,
    BookingFeedback, BookingFile, DocumentType
)
from bookings.serializers import (
    BookingDetailSerializer, BookingHistorySerializer,
    BookingFeedbackSerializer, BookingFileSerializer, BookingListSerializer
)
from .serializers import (
    ApprovalActionSerializer, DocumentVerificationSerializer,
    StaffCommentSerializer
)
from .permissions import IsStaffOrAdmin, CanApproveBookings
from accounts.models import StaffProfile

class ApprovalViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsStaffOrAdmin]
    serializer_class = BookingDetailSerializer
    filterset_fields = ['status', 'venue__category', 'venue__handled_by']
    search_fields = ['title', 'booking_code', 'user__email']
    ordering_fields = ['created_at', 'start_time', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user

        queryset = Booking.objects.filter(requires_approval=True)
        if user.user_type == 'staff':
            staff_profile = StaffProfile.objects.get(user=user)
            if staff_profile.department:
                department = staff_profile.department
                queryset = queryset.filter(venue__handled_by=department)
        elif user.user_type == 'student':
            queryset = queryset.filter(user=user)

        return queryset

    def get_serializer_class(self):
        if action in ['retrieve', 'destroy', 'partial-update', 'update']:
            return BookingDetailSerializer
        return BookingListSerializer

    @action(detail=False, methods=['get'])
    def pending(self, request):
        queryset = self.get_queryset().filter(status=BookingStatus.PENDING)
        return self._paginated_response(queryset)

    @action(detail=False, methods=['get'])
    def under_review(self, request):
        queryset = self.get_queryset().filter(status=BookingStatus.UNDER_REVIEW)
        return self._paginated_response(queryset)

    @action(detail=False, methods=['get'])
    def documents_pending(self, request):
        queryset = self.get_queryset().filter(status=BookingStatus.DOCUMENTS_PENDING)
        return self._paginated_response(queryset)

    def _paginated_response(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class BookingApprovalActionView(APIView):
    permission_classes = [CanApproveBookings]

    def get_booking(self, booking_id):
        return get_object_or_404(Booking, id=booking_id, requires_approval=True)

    def post(self, request, booking_id, action):
        booking = self.get_booking(booking_id)
        valid_actions = ['review', 'approve', 'reject', 'request-documents']
        if action not in valid_actions:
            return Response(
                {'error': f'Invalid action. Must be one of {valid_actions}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = ApprovalActionSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        comment = serializer.validated_data.get('comment', '')
        previous_status = booking.status

        if action == 'review':
            booking.status = BookingStatus.UNDER_REVIEW
        elif action == 'approve':
            booking.status = BookingStatus.APPROVED
            booking.approved_by = request.user
            booking.approval_date = timezone.now()
        elif action == 'reject':
            print("----reject**----")
            booking.status = BookingStatus.REJECTED
        elif action == 'request-documents':
            booking.status = BookingStatus.DOCUMENTS_PENDING

        booking.save()

        history_entry = BookingHistory.objects.create(
            booking=booking,
            previous_status=previous_status,
            new_status=booking.status,
            changed_by=request.user,
            comment=comment,
            handled_by_role=getattr(request.user, 'role', 'staff')
        )

        if comment:
            feedback_type = 'approval' if action == 'approve' else 'rejection' if action == 'reject' else 'requirement'
            BookingFeedback.objects.create(
                booking=booking,
                staff=request.user,
                content=comment,
                is_internal=False,
                feedback_type=feedback_type
            )

        return Response({
            'status': 'success',
            'action': action,
            'booking_status': booking.status,
            'history_id': history_entry.id
        })


class BookingApprovalHistoryView(APIView):
    permission_classes = [IsStaffOrAdmin]

    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)
        history = BookingHistory.objects.filter(booking=booking).order_by('-timestamp')
        serializer = BookingHistorySerializer(history, many=True)
        return Response(serializer.data)


class BookingCommentsView(APIView):
    permission_classes = [IsStaffOrAdmin]

    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)
        comments = BookingFeedback.objects.filter(booking=booking)

        if not request.user.is_staff:
            comments = comments.filter(is_internal=False)

        serializer = BookingFeedbackSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)

        serializer = StaffCommentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        comment = BookingFeedback.objects.create(
            booking=booking,
            staff=request.user,
            content=serializer.validated_data['content'],
            is_internal=serializer.validated_data['is_internal'],
            feedback_type=serializer.validated_data['feedback_type']
        )

        return Response(
            BookingFeedbackSerializer(comment).data,
            status=status.HTTP_201_CREATED
        )


class DocumentVerificationView(APIView):
    permission_classes = [IsStaffOrAdmin]

    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)
        documents = BookingFile.objects.filter(booking=booking)
        serializer = BookingFileSerializer(documents, many=True)
        return Response(serializer.data)

    def post(self, request, booking_id, document_id):
        document = get_object_or_404(BookingFile, id=document_id, booking_id=booking_id)

        serializer = DocumentVerificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        document.is_verified = True
        document.verified_by = request.user
        document.verified_at = timezone.now()
        document.save()

        booking = document.booking
        all_verified = not BookingFile.objects.filter(
            booking=booking,
            is_verified=False
        ).exists()

        if all_verified and booking.status == BookingStatus.DOCUMENTS_PENDING:
            previous_status = booking.status
            booking.status = BookingStatus.PENDING
            booking.documents_verified = True
            booking.save()

            BookingHistory.objects.create(
                booking=booking,
                previous_status=previous_status,
                new_status=booking.status,
                changed_by=request.user,
                comment="All required documents verified"
            )

        return Response({
            'status': 'success',
            'is_verified': document.is_verified,
            'verified_at': document.verified_at,
            'all_documents_verified': all_verified
        })
