""""""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ApprovalViewSet, BookingApprovalActionView, BookingApprovalHistoryView,
    BookingCommentsView, DocumentVerificationView
)

router = DefaultRouter()
router.register(r'approvals', ApprovalViewSet, basename='approval')

urlpatterns = [
    # ViewSet routes for listing approvals
    path('', include(router.urls)),

    # Approval action endpoints
    path('<int:booking_id>/review/', BookingApprovalActionView.as_view(), {'action': 'review'},
         name='approval-review'),
    path('<int:booking_id>/approve/', BookingApprovalActionView.as_view(), {'action': 'approve'},
         name='approval-approve'),
    path('<int:booking_id>/reject/', BookingApprovalActionView.as_view(), {'action': 'reject'},
         name='approval-reject'),
    path('<int:booking_id>/request-documents/', BookingApprovalActionView.as_view(), {'action': 'request-documents'},
         name='approval-request-documents'),

    # Approval history
    path('<int:booking_id>/history/', BookingApprovalHistoryView.as_view(), name='approval-history'),

    # Staff comments
    path('<int:booking_id>/comment/', BookingCommentsView.as_view(), name='approval-comment'),
    path('<int:booking_id>/comments/', BookingCommentsView.as_view(), name='approval-comments-list'),

    # Document verification
    path('<int:booking_id>/documents/', DocumentVerificationView.as_view(), name='approval-documents'),
    path('<int:booking_id>/documents/<int:document_id>/verify/', DocumentVerificationView.as_view(),
         name='approval-document-verify')
]
"""
# List bookings pending approval (filtered by staff role)
GET     /api/approvals/                         # Get all bookings that need review/approval

# Get bookings by status for approval management
GET     /api/approvals/pending/                 # Get all pending approvals
GET     /api/approvals/under-review/            # Get all bookings under review
GET     /api/approvals/documents-pending/       # Get all bookings waiting for documents

# Approval action endpoints
POST    /api/approvals/{booking_id}/review/     # Mark booking as under review
POST    /api/approvals/{booking_id}/approve/    # Approve a booking
POST    /api/approvals/{booking_id}/reject/     # Reject a booking
POST    /api/approvals/{booking_id}/request-documents/  # Request additional documents

# Approval workflow history
GET     /api/approvals/{booking_id}/history/    # Get approval history for a booking

# Staff feedback and comments
POST    /api/approvals/{booking_id}/comment/    # Add staff comment/feedback
GET     /api/approvals/{booking_id}/comments/   # Get all comments for a booking

# Document verification endpoints
GET     /api/approvals/{booking_id}/documents/  # Get documents for verification
POST    /api/approvals/{booking_id}/documents/{document_id}/verify/  # Verify a document
"""
