from rest_framework import serializers
from django.contrib.auth import get_user_model
from bookings.models import BookingHistory, BookingFeedback, BookingFile
from accounts.serializers import UserMinimalSerializer

User = get_user_model()


class ApprovalActionSerializer(serializers.Serializer):
    comment = serializers.CharField(required=False, allow_blank=True)


class DocumentVerificationSerializer(serializers.Serializer):
    verification_note = serializers.CharField(required=False, allow_blank=True)


class StaffCommentSerializer(serializers.Serializer):
    content = serializers.CharField(required=True)
    is_internal = serializers.BooleanField(default=True)
    feedback_type = serializers.ChoiceField(
        choices=[
            ('general', 'General Feedback'),
            ('rejection', 'Rejection Reason'),
            ('approval', 'Approval Notes'),
            ('requirement', 'Additional Requirements')
        ],
        default='general'
    )


class ApprovalHistorySerializer(serializers.ModelSerializer):
    changed_by = UserMinimalSerializer(read_only=True)

    class Meta:
        model = BookingHistory
        fields = [
            'id', 'previous_status', 'new_status',
            'changed_by', 'timestamp', 'comment', 'handled_by_role'
        ]


class ApprovalFeedbackSerializer(serializers.ModelSerializer):
    staff = UserMinimalSerializer(read_only=True)

    class Meta:
        model = BookingFeedback
        fields = [
            'id', 'staff', 'content', 'is_internal',
            'feedback_type', 'created_at'
        ]


class DocumentForApprovalSerializer(serializers.ModelSerializer):
    verified_by = UserMinimalSerializer(read_only=True)

    class Meta:
        model = BookingFile
        fields = [
            'id', 'file', 'file_name', 'file_type',
            'document_type', 'description', 'uploaded_at',
            'is_verified', 'verified_by', 'verified_at'
        ]