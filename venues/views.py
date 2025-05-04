from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime
from .models import Venue, VenueAvailability
from .serializers import (
    VenueSerializer,
    VenueDetailSerializer,
    VenueAvailabilitySerializer
)
from accounts.permissions import IsStaffOrReadOnly


class VenueViewSet(viewsets.ModelViewSet):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_available', 'handled_by']
    search_fields = ['name', 'description', 'location']
    ordering_fields = ['name', 'capacity']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return VenueDetailSerializer
        return VenueSerializer

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        venue = self.get_object()
        availability = VenueAvailability.objects.filter(venue=venue)

        date_param = request.query_params.get('date', None)
        if date_param:
            try:
                filter_date = datetime.strptime(date_param, '%Y-%m-%d').date()
                availability = availability.filter(date=filter_date)
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = VenueAvailabilitySerializer(availability, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsStaffOrReadOnly, IsAuthenticated],)
    def availability(self, request, pk=None):
        venue = self.get_object()

        if isinstance(request.data, list):
            serializer = VenueAvailabilitySerializer(data=request.data, many=True)

            if serializer.is_valid():
                for item in serializer.validated_data:
                    item['venue'] = venue

                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        copy = data.copy()
        copy['venue'] = venue.id

        serializer = VenueAvailabilitySerializer(data=copy)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path=r'availability/(?P<date>\d{4}-\d{2}-\d{2})',
            permission_classes=[IsAuthenticated, IsAdminUser])
    def delete_availability(self, request, pk=None, date=None):
        venue = self.get_object()

        try:
            filter_date = datetime.strptime(date, '%Y-%m-%d').date()
            deleted, _ = VenueAvailability.objects.filter(venue=venue, date=filter_date).delete()

            if deleted:
                return Response(
                    {'message': f'Deleted {deleted} availability slots for {date}'},
                    status=status.HTTP_200_OK
                )
            return Response(
                {'message': f'No availability slots found for {date}'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def search(self, request):
        queryset = self.get_queryset()

        category_id = request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(category__id=category_id)

        min_capacity = request.query_params.get('min_capacity', None)
        if min_capacity and min_capacity.isdigit():
            queryset = queryset.filter(capacity__gte=int(min_capacity))

        max_capacity = request.query_params.get('max_capacity', None)
        if max_capacity and max_capacity.isdigit():
            queryset = queryset.filter(capacity__lte=int(max_capacity))

        location = request.query_params.get('location', None)
        if location:
            queryset = queryset.filter(location__icontains=location)

        handled_by = request.query_params.get('handled_by', None)
        if handled_by:
            queryset = queryset.filter(handled_by=handled_by)

        feature = request.query_params.get('feature', None)
        if feature:
            # try:
            #     queryset = queryset.filter(features__contains={feature: True})
            # except Exception:
            venues_with_feature = []
            for venue in queryset:
                if feature in venue.features and venue.features.get(feature) is True:
                    venues_with_feature.append(venue.id)
            queryset = queryset.filter(id__in=venues_with_feature)

        serializer = VenueSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes = [IsAuthenticated])
    def available(self, request):
        date_str = request.query_params.get('date', None)
        start_time_str = request.query_params.get('start_time', None)
        end_time_str = request.query_params.get('end_time', None)

        if not all([date_str, start_time_str, end_time_str]):
            return Response(
                {'error': 'Missing required parameters: date, start_time, end_time'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()

            available_venues = Venue.objects.filter(
                is_available=True,
                availability__date=filter_date,
                availability__start_time__lte=start_time_str,
                availability__end_time__gte=end_time_str,
                availability__is_available=True
            ).distinct()

            serializer = VenueSerializer(available_venues, many=True)
            return Response(serializer.data)

        except ValueError:
            return Response(
                {'error': 'Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time'},
                status=status.HTTP_400_BAD_REQUEST
            )
