import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from accounts.models import StudentProfile, StaffProfile, AdminProfile
from accounts.serializers import StaffProfileSerializer, AdminProfileSerializer, StudentProfileSerializer, \
    UserSerializer


@pytest.mark.django_db
class TestRegisterView:
    url = reverse('register')

    def test_user_registration_success(self, api_client):
        data = {
            'email': 'newuser@example.com',
            'password': 'StrongPass123!',
            'user_type': 'STUDENT'
        }

        response = api_client.post(self.url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'tokens' in response.data
        assert 'user_id' in response.data
        assert response.data['status'] == 'success'
        assert User.objects.filter(email='newuser@example.com').exists()

    def test_user_registration_invalid_data(self, api_client):
        data = {
            'email': 'invalid-email',
            'password': 'weak',
            'user_type': 'INVALID'
        }

        response = api_client.post(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['status'] == 'error'
        assert 'errors' in response.data

@pytest.mark.django_db
class TestLoginView:
    url = reverse('login')

    def test_login_success(self, api_client, create_user):
        user = create_user()
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }

        response = api_client.post(self.url, data)
        print(response.data)
        assert response.status_code == status.HTTP_200_OK
        assert 'tokens' in response.data
        assert 'refresh' in response.data['tokens']
        assert 'user_id' in response.data
        assert response.data['user_type'] == 'student'

    def test_login_invalid_credentials(self, api_client, create_user):
        user = create_user()
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }

        response = api_client.post(self.url, data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'errors' in response.data
        assert response.data['status'] == 'error'

@pytest.mark.django_db
class TestUserProfileView:
    url = reverse('profile')

    def test_get_profile_authenticated(self, api_client, create_user):
        user = create_user()
        api_client.force_authenticate(user=user)

        response = api_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 'test@example.com'
        assert response.data['profile'] is not None

    def test_get_profile_unauthenticated(self, api_client):
        response = api_client.get(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestLogout:
    def test_logout(self, api_client, create_user, registered_user_data):
        logout_url = reverse('logout')
        profile_url = reverse('profile')
        token_verify_url = reverse('token_verify')
        token_refresh_url = reverse('token_refresh')

        user = create_user(**registered_user_data)

        login_data = {
            'email': registered_user_data['email'],
            'password': registered_user_data['password']
        }
        login_response = api_client.post(reverse('token_obtain_pair'), login_data)
        access_token = login_response.data['access']
        refresh_token = login_response.data['refresh']

        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        profile_response = api_client.get(profile_url)
        assert profile_response.status_code == status.HTTP_200_OK

        logout_response = api_client.post(
            logout_url,
            {'refresh': refresh_token},
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        assert logout_response.status_code == status.HTTP_205_RESET_CONTENT

        verify_response = api_client.post(
            token_verify_url,
            {'token': refresh_token},
        )
        assert verify_response.status_code == status.HTTP_400_BAD_REQUEST
        assert verify_response.data['non_field_errors'][0] == "Token is blacklisted"

        refresh_response = api_client.post(
            token_refresh_url,
            {'refresh': refresh_token},
        )
        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED
