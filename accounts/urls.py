from django.urls import path
from .views import (
    RegisterView, UserProfileView, CustomTokenObtainPairView, LogoutView, ProfileImageUploadView
)


urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('me/profile/', UserProfileView.as_view(), name='profile'),
    path('me/profile/picture/', ProfileImageUploadView.as_view(), name='profile-image-upload'),
]
