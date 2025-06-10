from rest_framework import serializers
from django.contrib.auth import get_user_model
from venues.models import Venue
from venues.serializers import VenueSerializer
from datetime import datetime
from .models import (
    Booking,
    EventDetail,
    BookingFile,
    BookingHistory,
    BookingFeedback,
    BookingStatus,
    DocumentType
)
from django.utils import timezone
from accounts.serializers import UserMinimalSerializer

User = get_user_model()


class BookingFileSerializer(serializers.ModelSerializer):
    document_type_display = serializers.CharField(source='document_type', read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = BookingFile
        fields = (
            'id', 'file', 'file_name', 'file_type', 'document_type',
            'document_type_display', 'description', 'uploaded_at',
            'is_verified', 'verified_by', 'verified_at', 'file_url'
        )
        read_only_fields = ('uploaded_at', 'is_verified', 'verified_by', 'verified_at')

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None

    def create(self, validated_data):
        booking_id = self.context.get('booking_id')
        if booking_id:
            validated_data['booking_id'] = booking_id
        return super().create(validated_data)


class EventDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventDetail
        fields = '__all__'

    def create(self, validated_data):
        booking_id = self.context.get('booking_id')
        if booking_id:
            validated_data['booking_id'] = booking_id
        return super().create(validated_data)


class BookingHistorySerializer(serializers.ModelSerializer):
    changed_by = UserMinimalSerializer(read_only=True)
    previous_status_display = serializers.CharField(source='get_previous_status_display', read_only=True)
    new_status_display = serializers.CharField(source='get_new_status_display', read_only=True)

    class Meta:
        model = BookingHistory
        fields = (
            'id', 'previous_status', 'previous_status_display',
            'new_status', 'new_status_display', 'changed_by',
            'timestamp', 'comment', 'handled_by_role'
        )
        read_only_fields = ('timestamp',)


class BookingFeedbackSerializer(serializers.ModelSerializer):
    staff = UserMinimalSerializer(read_only=True)
    feedback_type_display = serializers.CharField(source='get_feedback_type_display', read_only=True)

    class Meta:
        model = BookingFeedback
        fields = (
            'id', 'staff', 'content', 'is_internal',
            'feedback_type', 'feedback_type_display', 'created_at'
        )
        read_only_fields = ('created_at',)

    def create(self, validated_data):
        booking_id = self.context.get('booking_id')
        request = self.context.get('request')

        if booking_id:
            validated_data['booking_id'] = booking_id

        if request and request.user.is_authenticated:
            validated_data['staff'] = request.user

        return super().create(validated_data)


class BookingListSerializer(serializers.ModelSerializer):
    venue_name = serializers.CharField(source='venue.name', read_only=True)
    venue_location = serializers.CharField(source='venue.location', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = (
            'id', 'booking_code', 'title', 'venue_name', 'venue_location',
            'start_time', 'end_time', 'status', 'status_display',
            'created_at', 'user_name', 'payment_required', 'payment_completed',
            'documents_required', 'documents_verified'
        )

    def get_user_name(self, obj):
        if obj.user.first_name and obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return obj.user.email


class BookingDetailSerializer(serializers.ModelSerializer):
    venue = VenueSerializer(read_only=True)
    venue_id = serializers.PrimaryKeyRelatedField(
        queryset=Venue.objects.all(),
        write_only=True,
        source='venue'
    )
    user = UserMinimalSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    files = BookingFileSerializer(many=True, read_only=True)
    event_detail = EventDetailSerializer(read_only=True)
    history = BookingHistorySerializer(many=True, read_only=True)
    feedback = serializers.SerializerMethodField()
    duration_hours = serializers.FloatField(read_only=True)

    class Meta:
        model = Booking
        fields = (
            'id', 'booking_code', 'user', 'venue', 'venue_id',
            'title', 'description', 'start_time', 'end_time',
            'attendees_count', 'status', 'status_display',
            'created_at', 'updated_at', 'payment_required',
            'payment_amount', 'payment_completed', 'payment_reference',
            'requires_approval', 'approved_by', 'approval_date',
            'documents_required', 'documents_verified',
            'files', 'event_detail', 'history', 'feedback',
            'duration_hours', 'is_past'
        )
        read_only_fields = (
            'booking_code', 'id', 'venue', 'venue_id',
            'payment_required', 'documents_required',
            'requires_approval', 'approved_by', 'approval_date', 'documents_verified',
            'is_past', 'duration_hours'
        )

    def get_feedback(self, obj):
        request = self.context.get('request')
        queryset = obj.feedback.all()

        if request and request.user.is_authenticated:
            if request.user.is_staff or request.user.is_superuser:
                return BookingFeedbackSerializer(queryset, many=True).data

        queryset = queryset.filter(is_internal=False)
        return BookingFeedbackSerializer(queryset, many=True).data

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        return super().create(validated_data)

    def validate(self, data):
        if data.get('time_slot') == 'custom':
            if not (data.get('start_time') and data.get('end_time')):
                raise serializers.ValidationError({
                    'start_time': 'Start time is required for custom time slot.',
                    'end_time': 'End time is required for custom time slot.'
                })
            date = data.get('date')
            start_time = data.get('start_time')
            end_time = data.get('end_time')
            try:
                if isinstance(start_time, str):
                    start_time = datetime.strptime(f"{date} {start_time}", '%Y-%m-%d %H:%M').time()
                    data['start_time'] = start_time
                if isinstance(end_time, str):
                    end_time = datetime.strptime(f"{date} {end_time}", '%Y-%m-%d %H:%M').time()
                    data['end_time'] = end_time
            except ValueError:
                raise serializers.ValidationError({
                    'start_time': 'Invalid time format. Use HH:MM.',
                    'end_time': 'Invalid time format. Use HH:MM.'
                })
        if data.get('attendees_count', 0) <= 0:
            raise serializers.ValidationError({
                'attendees_count': 'Attendees count must be greater than zero.'
            })
        return data


class BookingStatusUpdateSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(required=False, write_only=True)
    handled_by_role = serializers.CharField(required=False, write_only=True)
    feedback = serializers.CharField(required=False, write_only=True)
    feedback_is_internal = serializers.BooleanField(required=False, write_only=True, default=True)
    feedback_type = serializers.CharField(required=False, write_only=True, default='general')

    class Meta:
        model = Booking
        fields = ('status', 'comment', 'handled_by_role', 'feedback', 'feedback_is_internal', 'feedback_type')

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None

        # Extract fields that don't belong to Booking model
        comment = validated_data.pop('comment', '')
        handled_by_role = validated_data.pop('handled_by_role', '')
        feedback_text = validated_data.pop('feedback', None)
        feedback_is_internal = validated_data.pop('feedback_is_internal', True)
        feedback_type = validated_data.pop('feedback_type', 'general')

        # Track old status for history
        old_status = instance.status
        new_status = validated_data.get('status', old_status)

        # Update booking status
        instance = super().update(instance, validated_data)

        # If status changed, create history record
        if old_status != new_status:
            BookingHistory.objects.create(
                booking=instance,
                previous_status=old_status,
                new_status=new_status,
                changed_by=user,
                comment=comment,
                handled_by_role=handled_by_role
            )

            # If status changed to APPROVED, update approval fields
            if new_status == BookingStatus.APPROVED and user:
                instance.approved_by = user
                instance.approval_date = timezone.now()
                instance.save(update_fields=['approved_by', 'approval_date'])

        # Create feedback if provided
        if feedback_text and user:
            BookingFeedback.objects.create(
                booking=instance,
                staff=user,
                content=feedback_text,
                is_internal=feedback_is_internal,
                feedback_type=feedback_type
            )

        return instance


class BookingCreateSerializer(serializers.ModelSerializer):
    venue_id = serializers.PrimaryKeyRelatedField(
        queryset=Venue.objects.all(),
        source='venue'
    )
    event_detail = EventDetailSerializer(required=False)

    class Meta:
        model = Booking
        fields = (
            'venue_id', 'title', 'description', 'start_time',
            'end_time', 'attendees_count', 'event_detail', 'id', 'booking_code'
        )

    def create(self, validated_data):
        # Extract event detail data if present
        event_detail_data = validated_data.pop('event_detail', None)

        # Set user from request
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user

        # Create booking
        booking = super().create(validated_data)

        # Create event detail if provided
        if event_detail_data:
            EventDetail.objects.create(booking=booking, **event_detail_data)

        return booking


class BookingCalendarSerializer(serializers.ModelSerializer):
    venue_name = serializers.CharField(source='venue.name', read_only=True)
    venue_location = serializers.CharField(source='venue.location', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    url = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = (
            'id', 'title', 'start_time', 'end_time', 'venue_name',
            'venue_location', 'status', 'status_display', 'url', 'color'
        )

    def get_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/api/bookings/{obj.id}/')
        return None

    def get_color(self, obj):
        status_colors = {
            'pending': '#FFC107',  # Amber
            'approved': '#4CAF50',  # Green
            'rejected': '#F44336',  # Red
            'cancelled': '#9E9E9E',  # Grey
            'completed': '#2196F3',  # Blue
            'under_review': '#FF9800',  # Orange
            'payment_pending': '#E91E63',  # Pink
            'documents_pending': '#673AB7',  # Deep Purple
        }
        return status_colors.get(obj.status, '#9C27B0')  # Default: Purple