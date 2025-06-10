import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from accounts.models import StudentProfile, StaffProfile


@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
class TestUnifiedProfileView:
    url = reverse('profile')

    def test_get_student_profile(self, api_client, create_user):
        student = create_user(
            user_type="student",
            profile_data={'major': 'Biology', 'year': 2}
        )
        api_client.force_authenticate(user=student)

        response = api_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == student.email
        assert response.data['profile']['major'] == 'Biology'
        assert response.data['profile']['year'] == 2

    def test_get_staff_profile(self, api_client, create_user):
        staff = create_user(
            email="staff@example.com",
            user_type="staff",
            profile_data={'department': 'SA'}
        )
        api_client.force_authenticate(user=staff)

        response = api_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 'staff@example.com'
        assert response.data['profile']['department'] == 'SA'

        delete_response = api_client.delete(self.url)

        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    def test_update_student_profile(self, api_client, create_user):
        student = create_user(
            user_type="student",
            first_name="Original",
            last_name="Student",
            profile_data={'major': 'Math', 'year': 1}
        )
        api_client.force_authenticate(user=student)

        update_data = {
            'first_name': 'Updated',
            'last_name': 'Student',
            'profile': {
                'major': 'Computer Science',
                'year': 3
            }
        }

        response = api_client.put(self.url, update_data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated'
        assert response.data['last_name'] == 'Student'
        assert response.data['profile']['major'] == 'Computer Science'
        assert response.data['profile']['year'] == 3

        student.refresh_from_db()
        assert student.first_name == 'Updated'
        assert student.last_name == 'Student'
        studentprofile = StudentProfile.objects.get(user=student)
        assert studentprofile.major == 'Computer Science'
        assert studentprofile.year == 3

        delete_response = api_client.delete(self.url)

        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    def test_update_staff_profile(self, api_client, create_user):
        staff = create_user(
            email="staff@example.com",
            user_type="staff",
            first_name="Original",
            last_name="Staff",
            profile_data={'department': 'PPK'}
        )
        api_client.force_authenticate(user=staff)

        update_data = {
            'first_name': 'Updated',
            'last_name': 'Staff',
            'profile': {
                'department': 'SA'
            }
        }

        response = api_client.put(self.url, update_data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated'
        assert response.data['last_name'] == 'Staff'
        assert response.data['profile']['department'] == 'SA'

        staff.refresh_from_db()
        assert staff.first_name == 'Updated'
        assert staff.last_name == 'Staff'
        staffprofile = StaffProfile.objects.get(user=staff)
        print(response.data)
        assert staffprofile.department == 'ppk'

        delete_response = api_client.delete(self.url)

        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    def test_update_profile_unauthorized(self, api_client, create_user):
        update_data = {
            'first_name': 'wrong',
            'last_name': 'name',
            'profile': {'major': 'Fail'}
        }
        response = api_client.put(self.url, update_data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_partial_update_profile(self, api_client, create_user):
        student = create_user(
            user_type="student",
            profile_data={'major': 'Physics', 'year': 2}
        )
        api_client.force_authenticate(user=student)

        update_data = {
            'profile': {
                'major': 'Chemistry'
            }
        }

        response = api_client.patch(self.url, update_data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['profile']['major'] == 'Chemistry'
        assert response.data['profile']['year'] == 2

        delete_response = api_client.delete(self.url)

        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

#
# @pytest.mark.django_db
# class TestProfileImageUpload:
#     @pytest.fixture
#     def default_image(self):
#         default_path = os.path.join(settings.BASE_DIR, "media/profile_pics/default_profilepic.jpg")
#
#         with open(default_path, 'rb') as image_io:
#             default_image_data = image_io.read()
#
#         return SimpleUploadedFile(
#             'default_profilepic.jpg',
#             default_image_data,
#             content_type='image/jpeg'
#         )
#
#     def test_upload_profile_image(self, api_client, create_user, default_image):
#         student = create_user(
#             user_type="student",
#             profile_data={'major': 'Biology', 'year': 2}
#         )
#         api_client.force_authenticate(user=student)
#
#         get_response = api_client.get(reverse('profile'))
#         initial_profile_pic = get_response.data['profile']['profile_picture']
#         test_image_path = os.path.join(settings.BASE_DIR, 'tests/test_image.jpeg')
#
#         with open(test_image_path, 'rb') as image:
#             test_image_data = image.read()
#
#         # Correct way to create InMemoryUploadedFile
#         from io import BytesIO
#         file_io = BytesIO(test_image_data)
#         test_image = InMemoryUploadedFile(
#             file=file_io,                          # file-like object
#             field_name='profile_picture',          # name of the form field
#             name='test_image.jpeg',                # name of the file
#             content_type='image/jpeg',             # content type
#             size=len(test_image_data),             # size of file
#             charset=None                           # character set (not needed for images)
#         )
#
#         url = reverse('profile')
#         response = api_client.put(
#             url,
#             {'profile_picture': test_image},
#             format='multipart'
#         )
#         assert response.status_code == status.HTTP_200_OK
#         assert 'profile' in response.data
#         assert 'profile_picture' in response.data['profile']
#
#         new_profile_pic = response.data['profile']['profile_picture']
#         assert new_profile_pic != initial_profile_pic
#
#         assert new_profile_pic.startswith('http')
#         assert 'test_image' in new_profile_pic.lower() or 'media' in new_profile_pic.lower()
#
#         if settings.DEFAULT_FILE_STORAGE != 'django.core.files.storage.InMemoryStorage':
#             media_path = new_profile_pic.split('/media/')[-1]
#             assert os.path.exists(os.path.join(settings.MEDIA_ROOT, media_path))
#
#     def test_invalid_image_upload(self, api_client, create_user):
#         student = create_user(user_type="student")
#         api_client.force_authenticate(user=student)
#
#         invalid_file = SimpleUploadedFile(
#             'invalid.txt',
#             b'This is not an image',
#             content_type='text/plain'
#         )
#
#         response = api_client.put(
#             reverse('profile'),
#             {'profile_picture': invalid_file},
#             format='multipart'
#         )
#
#         assert response.status_code == status.HTTP_400_BAD_REQUEST
#         assert 'profile_picture' in response.data
#         assert 'Upload a valid image' in str(response.data['profile_picture'])