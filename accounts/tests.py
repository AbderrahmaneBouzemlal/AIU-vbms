from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import User, StudentProfile, StaffProfile, AdminProfile


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