from django.contrib.auth import user_logged_in

from .models import User, StudentProfile, StaffProfile, AdminProfile
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError
from .serializers import UserSerializer, UserRegistrationSerializer, CustomTokenObtainSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user_id = serializer.validated_data['user_id']
            user = User.objects.get(id=user_id)
            refresh = RefreshToken.for_user(user)
            return Response({
                'status': 'success',
                'message': 'User logged in successfully',
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                'user_id': user_id,
                'user_type': user.user_type
            })
        except ValidationError as e:
            return Response({
                'status': 'error',
                'message': 'Validation failed',
                'errors': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred',
                'errors': {'detail': str(e)}
            }, status=status.HTTP_401_UNAUTHORIZED)


from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {"detail": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            RefreshToken(refresh_token).blacklist()
            auth_header = request.headers.get('Authorization', '').split()
            if len(auth_header) == 2 and auth_header[0].lower() == 'bearer':
                access_token = auth_header[1]
                try:
                    AccessToken(access_token).set_exp(lifetime=timezone.timedelta(seconds=0))
                except TokenError:
                    pass

            return Response(
                {"detail": "Successfully logged out"},
                status=status.HTTP_205_RESET_CONTENT
            )

        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class RegisterView(APIView):
    permission_classes = []
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'status': 'success',
                'message': 'User registered successfully',
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                'user_id': user.id,
                'user_type': user.user_type
            }, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({
                'status': 'error',
                'message': 'Validation failed',
                'errors': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred',
                'errors': {'detail': str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        user = request.user
        serialized_user = self.serializer_class(user)
        data = serialized_user.data

        return Response(data)

    def put(self, request):
        user = request.user
        user_serializer = self.serializer_class(user, data=request.data, partial=True)
        user_serializer.is_valid(raise_exception=True)
        user_instance = user_serializer.save()

        return self.get(request)

    def patch(self, request):
        return self.put(request)

    def delete(self, request):
        user = request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

