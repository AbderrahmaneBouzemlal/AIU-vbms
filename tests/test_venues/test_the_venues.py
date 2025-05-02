import pytest
import json
from datetime import date, time, timedelta
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from venues.models import VenueCategory, Venue, VenueAvailability

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def staff_user():
    user = User.objects.create_user(
        email='staff@example.com',
        password='testpass123',
        user_type='STAFF',
        is_staff=True
    )
    return user


@pytest.fixture
def normal_user():
    user = User.objects.create_user(
        email='user@example.com',
        password='testpass123',
        user_type='student'
    )
    return user


@pytest.fixture
def venue_category():
    return VenueCategory.objects.create(
        name='Convocation Hall',
        description='Large hall for conferences and events'
    )


@pytest.fixture
def venue(venue_category):
    return Venue.objects.create(
        name='Grand Hall',
        description='Spacious venue for large events',
        capacity=500,
        location='Downtown',
        category=venue_category,
        handled_by='sa',
        is_available=True,
        features={
            'projector': True,
            'sound_system': True,
            'catering': False
        }
    )


@pytest.fixture
def venue_availability(venue):
    tomorrow = date.today() + timedelta(days=1)
    return VenueAvailability.objects.create(
        venue=venue,
        date=tomorrow,
        start_time=time(9, 0),
        end_time=time(17, 0),
        is_available=True
    )

@pytest.mark.django_db
class TestVenueCategoryEndpoints:

    def test_list_venue_categories(self, api_client, venue_category):
        url = reverse('venuecategory-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == venue_category.name

    def test_create_venue_category_as_staff(self, api_client, staff_user):
        api_client.force_authenticate(user=staff_user)
        url = reverse('venuecategory-list')

        payload = {
            'name': 'Exhibition Hall',
            'description': 'Space for exhibitions and trade shows'
        }

        response = api_client.post(url, payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == payload['name']
        assert VenueCategory.objects.filter(name=payload['name']).exists()

    def test_create_venue_category_as_normal_user_fails(self, api_client, normal_user):
        api_client.force_authenticate(user=normal_user)
        url = reverse('venuecategory-list')

        payload = {'name': 'Meeting Room'}

        response = api_client.post(url, payload)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not VenueCategory.objects.filter(name=payload['name']).exists()

    def test_retrieve_venue_category_detail(self, api_client, venue_category):
        url = reverse('venuecategory-detail', args=[venue_category.id])
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == venue_category.name
        assert response.data['description'] == venue_category.description

    def test_update_venue_category_as_staff(self, api_client, staff_user, venue_category):
        api_client.force_authenticate(user=staff_user)
        url = reverse('venuecategory-detail', args=[venue_category.id])

        payload = {'name': 'Updated Category Name'}

        response = api_client.patch(url, payload)
        venue_category.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert venue_category.name == payload['name']

    def test_delete_venue_category_as_staff(self, api_client, staff_user, venue_category):
        api_client.force_authenticate(user=staff_user)
        url = reverse('venuecategory-detail', args=[venue_category.id])

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not VenueCategory.objects.filter(id=venue_category.id).exists()

@pytest.mark.django_db
class TestVenueEndpoints:

    def test_list_venues(self, api_client, venue):
        url = reverse('venue-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == venue.name

    def test_filter_venues_by_category(self, api_client, venue, venue_category):
        url = f"{reverse('venue-list')}?category={venue_category.id}"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == venue.id

    def test_search_venues(self, api_client, venue):
        url = f"{reverse('venue-list')}?search=Grand"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == venue.id

    def test_create_venue_as_staff(self, api_client, staff_user, venue_category):
        api_client.force_authenticate(user=staff_user)
        url = reverse('venue-list')

        payload = {
            'name': 'Small Meeting Room',
            'description': 'Cozy space for small meetings',
            'capacity': 20,
            'location': 'East Wing',
            'category': venue_category.id,
            'handled_by': 'ppk',
            'is_available': True,
            'features': {'whiteboard': True, 'coffee': True}
        }

        response = api_client.post(url, json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Venue.objects.filter(name=payload['name']).exists()

    def test_retrieve_venue_detail(self, api_client, venue):
        url = reverse('venue-detail', args=[venue.id])
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == venue.name
        assert 'category' in response.data
        assert isinstance(response.data['category'], dict)
        assert 'availability' in response.data

    def test_update_venue_as_staff(self, api_client, staff_user, venue):
        api_client.force_authenticate(user=staff_user)
        url = reverse('venue-detail', args=[venue.id])

        payload = {'capacity': 600}

        response = api_client.patch(url, payload)
        venue.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert venue.capacity == payload['capacity']

    def test_delete_venue_as_staff(self, api_client, staff_user, venue):
        api_client.force_authenticate(user=staff_user)
        url = reverse('venue-detail', args=[venue.id])

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Venue.objects.filter(id=venue.id).exists()

    def test_venue_advanced_search(self, api_client, venue):
        url = reverse('venue-search')

        query_params = {
            'min_capacity': 400,
            'location': 'Downtown',
        }
        response = api_client.get(url, query_params)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == venue.id

        query_params = {'feature': 'projector'}
        response = api_client.get(url, query_params)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == venue.id

        query_params = {'feature': 'swimming_pool'}
        response = api_client.get(url, query_params)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

        response = api_client.get(url, {'min_capacity': 1000})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

@pytest.mark.django_db
class TestVenueAvailabilityEndpoints:
    # def test_get_venue_availability(self, api_client, venue, venue_availability, create_user, registered_user_data):
    #     url = reverse('venue-available', args=[venue.id])
    #     user = create_user(**registered_user_data)
    #     api_client.force_authenticate(user=user)
    #     response = api_client.get(url)
    #
    #     assert response.status_code == status.HTTP_200_OK
    #     assert len(response.data) == 1
    #     assert response.data[0]['venue'] == venue.id

    def test_create_venue_availability_as_staff(self, api_client, staff_user, venue):
        api_client.force_authenticate(user=staff_user)
        url = reverse('venue-availability', args=[venue.id])

        next_week = date.today() + timedelta(days=7)
        payload = {
            'date': next_week.isoformat(),
            'start_time': '10:00:00',
            'end_time': '18:00:00',
            'is_available': True
        }

        response = api_client.post(url, payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert VenueAvailability.objects.filter(venue=venue, date=next_week).exists()

    def test_create_batch_venue_availability(self, api_client, staff_user, venue):
        api_client.force_authenticate(user=staff_user)
        url = reverse('venue-availability', args=[venue.id])

        next_week = date.today() + timedelta(days=7)
        next_day = next_week + timedelta(days=1)

        payload = [
            {
                'venue': venue.id,
                'date': next_week.isoformat(),
                'start_time': '10:00:00',
                'end_time': '14:00:00',
                'is_available': True
            },
            {
                'venue': venue.id,
                'date': next_day.isoformat(),
                'start_time': '12:00:00',
                'end_time': '16:00:00',
                'is_available': True
            }
        ]

        response = api_client.post(url, json.dumps(payload), content_type='application/json')

        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.data) == 2
        assert VenueAvailability.objects.filter(venue=venue, date=next_week).exists()
        assert VenueAvailability.objects.filter(venue=venue, date=next_day).exists()

    def test_delete_venue_availability_by_date(self, api_client, staff_user, venue, venue_availability):
        api_client.force_authenticate(user=staff_user)
        date_str = venue_availability.date.strftime('%Y-%m-%d')
        url = reverse('venue-delete-availability', args=[venue.id, date_str])

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_200_OK
        assert not VenueAvailability.objects.filter(venue=venue, date=venue_availability.date).exists()

    def test_get_available_venues(self, api_client, venue, venue_availability, normal_user):
        api_client.force_authenticate(user=normal_user)
        url = reverse('venue-available')

        query_params = {
            'date': venue_availability.date.isoformat(),
            'start_time': '10:00',
            'end_time': '16:00'
        }

        response = api_client.get(url, query_params)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == venue.id

    def test_get_available_venues_invalid_params(self, api_client, normal_user):
        url = reverse('venue-available')
        api_client.force_authenticate(user=normal_user)

        response = api_client.get(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        response = api_client.get(url, {
            'date': 'not-a-date',
            'start_time': '10:00:00',
            'end_time': '16:00:00'
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST