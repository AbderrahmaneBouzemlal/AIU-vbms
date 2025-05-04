from rest_framework import viewsets, generics, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from accounts.permissions import IsOwnerOrStaff, IsStaffOrReadOnly
from .permissions import CanManageBooking
from django.db.models import Q

from .models import (
    Booking,
    EventDetail,
    BookingFile,
    BookingFeedback,
    BookingHistory,
    BookingStatus,
    DocumentType
)
from .serializers import (
    BookingListSerializer,
    BookingDetailSerializer,
    BookingCreateSerializer,
    BookingStatusUpdateSerializer,
    EventDetailSerializer,
    BookingFileSerializer,
    BookingFeedbackSerializer,
    BookingHistorySerializer,
    BookingCalendarSerializer
)


class BookingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'venue', 'payment_completed', 'documents_verified']
    search_fields = ['title', 'description', 'booking_code', 'venue__name']
    ordering_fields = ['created_at', 'start_time', 'end_time', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return Booking.objects.all()

        return Booking.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action == 'list':
            return BookingListSerializer
        elif self.action == 'create':
            return BookingCreateSerializer
        elif self.action == 'update_status':
            return BookingStatusUpdateSerializer
        return BookingDetailSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsOwnerOrStaff]
        elif self.action == 'update_status':
            self.permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
        return super().get_permissions()

    def perform_destroy(self, instance):
        # Instead of deleting, change status to cancelled
        instance.status = BookingStatus.CANCELLED
        instance.save()

        # Create history record for cancellation
        BookingHistory.objects.create(
            booking=instance,
            previous_status=instance.status,
            new_status=BookingStatus.CANCELLED,
            changed_by=self.request.user,
            comment="Booking cancelled by user"
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Only allow updates if booking is still pending
        if instance.status != BookingStatus.PENDING:
            return Response(
                {"detail": "Cannot update booking that is not in pending status."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['put'], url_path='status')
    def update_status(self, request, pk=None):
        booking = self.get_object()
        serializer = self.get_serializer(booking, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            # Return the updated booking using the detail serializer
            return Response(BookingDetailSerializer(booking, context={'request': request}).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='history')
    def history(self, request, pk=None):
        # Only staff can view history
        if not request.user.is_staff and not request.user.is_superuser:
            raise PermissionDenied("Only staff members can view booking history.")

        booking = self.get_object()
        history = booking.history.all().order_by('-timestamp')
        serializer = BookingHistorySerializer(history, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='feedback')
    def add_feedback(self, request, pk=None):
        booking = self.get_object()

        # Only staff can add feedback
        if not request.user.is_staff and not request.user.is_superuser:
            raise PermissionDenied("Only staff members can add feedback.")

        serializer = BookingFeedbackSerializer(
            data=request.data,
            context={'request': request, 'booking_id': booking.pk}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventDetailViewSet(viewsets.GenericViewSet):
    """
    ViewSet for managing event details associated with a booking.
    """
    permission_classes = [IsAuthenticated, CanManageBooking]
    serializer_class = EventDetailSerializer

    def get_booking(self):
        booking_id = self.kwargs.get('booking_pk')
        return get_object_or_404(Booking, pk=booking_id)

    def retrieve(self, request, booking_pk=None, pk=None):
        booking = self.get_booking()
        # Check if booking has event details
        if not hasattr(booking, 'event_detail'):
            return Response(
                {"detail": "No event details found for this booking."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(booking.event_detail)
        return Response(serializer.data)

    def create(self, request, booking_pk=None):
        booking = self.get_booking()

        # Check if event details already exist
        if hasattr(booking, 'event_detail'):
            return Response(
                {"detail": "Event details already exist for this booking."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(
            data=request.data,
            context={'booking_id': booking.pk}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, booking_pk=None, pk=None):
        booking = self.get_booking()

        # Check if event details exist
        if not hasattr(booking, 'event_detail'):
            return Response(
                {"detail": "No event details found for this booking."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(
            booking.event_detail,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookingFileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, CanManageBooking]
    serializer_class = BookingFileSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        booking_id = self.kwargs.get('booking_pk')
        return BookingFile.objects.filter(booking_id=booking_id)

    def perform_create(self, serializer):
        booking_id = self.kwargs.get('booking_pk')
        serializer.save(
            booking_id=booking_id,
            uploaded_by=self.request.user
        )

    @action(detail=True, methods=['get'], url_path='download')
    def download_file(self, request, booking_pk=None, pk=None):
        file_obj = self.get_object()
        return FileResponse(file_obj.file, as_attachment=True, filename=file_obj.file_name)

    @action(detail=True, methods=['post'], url_path='verify')
    def verify_file(self, request, booking_pk=None, pk=None):
        if not request.user.is_staff and not request.user.is_superuser:
            raise PermissionDenied("Only staff members can verify documents.")

        file_obj = self.get_object()
        file_obj.is_verified = True
        file_obj.verified_by = request.user
        file_obj.verified_at = timezone.now()
        file_obj.save()

        serializer = self.get_serializer(file_obj)
        return Response(serializer.data)


class CalendarViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for calendar views of bookings.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = BookingCalendarSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'venue']

    def get_queryset(self):
        # Base queryset - filter by date range if provided
        start_date = self.request.query_params.get('start')
        end_date = self.request.query_params.get('end')

        queryset = Booking.objects.all()

        if start_date:
            queryset = queryset.filter(end_time__gte=start_date)
        if end_date:
            queryset = queryset.filter(start_time__lte=end_date)

        return queryset

    def list(self, request):
        # For staff, return all bookings
        if request.user.is_staff or request.user.is_superuser:
            queryset = self.filter_queryset(self.get_queryset())
        else:
            # For regular users, show public approved bookings and their own
            queryset = self.filter_queryset(
                self.get_queryset().filter(
                    Q(status=BookingStatus.APPROVED) | Q(user=request.user)
                )
            )

        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='venue/(?P<venue_id>[^/.]+)')
    def venue_calendar(self, request, venue_id=None):
        queryset = self.filter_queryset(self.get_queryset().filter(venue_id=venue_id))

        # For non-staff, only show approved bookings and their own
        if not (request.user.is_staff or request.user.is_superuser):
            queryset = queryset.filter(
                Q(status=BookingStatus.APPROVED) | Q(user=request.user)
            )

        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='user')
    def user_calendar(self, request):
        # Only show the current user's bookings
        queryset = self.filter_queryset(self.get_queryset().filter(user=request.user))
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)