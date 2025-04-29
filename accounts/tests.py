import os
import pytest
import tempfile
from PIL import Image
from django.urls import reverse
from django.conf import settings
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import User, StudentProfile, StaffProfile


class AccountsTests(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            email='student@test.com',
            password='testpass123',
            user_type='student'
        )

        self.staff = User.objects.create_user(
            email='staff@test.com',
            password='testpass123',
            user_type='staff'
        )

        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='testpass123',
            user_type='admin'
        )
        self.client = APIClient()

    def test_user_registration(self):
        url = reverse('register')
        data = {
            'email': 'newstudent@gmail.com',
            'password': 'newpass123',
            'user_type': 'student',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('user_id', response.data)
        self.assertEqual(response.data['user_type'], 'student')

        user = User.objects.get(email='newstudent@gmail.com')
        try:
            student_profile = StudentProfile.objects.get(user=user)
        except StudentProfile.DoesNotExist:
            self.fail('StudentProfile was not created')



    def test_user_login(self):
        url = reverse('login')
        data = {
            'email':'student@test.com',
            'password':'testpass123'
        }
        response = self.client.post(url, data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        self.assertEqual(response.data['user_type'], 'student')

    def test_get_profile(self):
        self.client.force_authenticate(user=self.student)
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_type'], 'student')
        self.assertIn('student_profile', response.data)
        self.assertNotIn('staff_profile', response.data)

    def test_update_student_profile(self):
        self.client.force_authenticate(user=self.student)
        url = reverse('student-profile')
        data = {
            'student_id': 'AIU22102201',
            'major': 'Computer Science'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.student.refresh_from_db()
        self.assertEqual(self.student.student_profile.student_id, 'AIU22102201')
        self.assertEqual(self.student.student_profile.major, 'Computer Science')

    def test_permissions(self):
        self.client.force_authenticate(user=self.staff)
        url = reverse('student-profile')
        response = self.client.put(url, {'student_id': 'S999'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)



@pytest.mark.django_db
class ProfileImageUploadTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('profile-image-upload')  # Update with your actual URL name

    def test_upload_profile_image(self):
        """Test uploading an image to user profile"""
        # Create a dummy image
        image = Image.new('RGB', (100, 100), color='red')
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file)
        tmp_file.seek(0)

        # Upload the image
        with open(tmp_file.name, 'rb') as file:
            upload_data = {'profile_picture': file}
            response = self.client.patch(self.url, upload_data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('profile_picture', response.data)
        self.assertTrue(response.data['profile_picture'].endswith('.jpg'))

        profile = StudentProfile.objects.get(user=self.user)
        self.assertTrue(os.path.exists(profile.profile_picture.path))

    def test_upload_invalid_file(self):
        # Create a dummy text file
        tmp_file = tempfile.NamedTemporaryFile(suffix='.txt')
        tmp_file.write(b'This is not an image')
        tmp_file.seek(0)

        with open(tmp_file.name, 'rb') as file:
            upload_data = {'profile_picture': file}
            response = self.client.patch(self.url, upload_data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('profile_picture', response.data)

    def test_remove_profile_image(self):
        """Test removing the profile image"""
        # First upload an image
        image = Image.new('RGB', (100, 100), color='blue')
        tmp_file = tempfile.NamedTemporaryFile(suffix='.png')
        image.save(tmp_file)
        tmp_file.seek(0)

        with open(tmp_file.name, 'rb') as file:
            upload_data = {'profile_picture': file}
            self.client.patch(self.url, upload_data, format='multipart')

        # Now remove the image
        response = self.client.patch(self.url, {'profile_picture': None}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['profile_picture'])

        # Verify the file was deleted from filesystem
        profile = StudentProfile.objects.get(user=self.user)
        self.assertFalse(hasattr(profile.profile_picture, 'path') or
                         not os.path.exists(profile.profile_picture.path))

    def tearDown(self):
        # Clean up any uploaded files
        for profile in StudentProfile.objects.all():
            if profile.profile_picture:
                if os.path.exists(profile.profile_picture.path):
                    os.remove(profile.profile_picture.path)

