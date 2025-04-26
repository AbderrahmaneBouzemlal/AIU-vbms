from rest_framework.decorators import api_view
from .models import User, StudentProfile, StaffProfile, AdminProfile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError
from .serializers import UserSerializer, UserRegistrationSerializer, CustomTokenObtainSerializer, \
    StudentProfileSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


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
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        data = serializer.data

        return Response(data)

    def put(self, request):
        user = request.user
        user_serializer = UserSerializer(user, data=request.data, partial=True)
        user_serializer.is_valid(raise_exception=True)
        user_instance = user_serializer.save()

        return self.get(request)

    def patch(self, request):
        return self.put(request)

