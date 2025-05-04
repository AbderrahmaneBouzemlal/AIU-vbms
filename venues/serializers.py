from rest_framework import serializers
from .models import Venue, VenueAvailability


class VenueAvailabilitySerializer(serializers.ModelSerializer):

    class Meta:
        model = VenueAvailability
        fields = ['id', 'venue', 'date', 'start_time', 'end_time', 'is_available']
        read_only_fields = ['id']


class VenueSerializer(serializers.ModelSerializer):

    class Meta:
        model = Venue
        fields = [
            'id', 'name', 'description', 'capacity',
            'location', 'category', 'handled_by',
            'is_available', 'features'
        ]
        read_only_fields = ['id']


class VenueDetailSerializer(serializers.ModelSerializer):
    availability = VenueAvailabilitySerializer(many=True, read_only=True)

    class Meta:
        model = Venue
        fields = [
            'id', 'name', 'description', 'capacity',
            'location', 'category', 'handled_by',
            'is_available', 'features', 'availability'
        ]