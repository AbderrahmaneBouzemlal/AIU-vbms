from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import User, StudentProfile, StaffProfile, AdminProfile, UserProfile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import os


class UploadProfilePicture(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('profile_picture',)

    def validate_profile_picture(self, value):
        if value:
            valid_extensions = ['.jpg', '.jpeg', '.png']
            ext = os.path.splitext(value.name)[1].lower()
            if ext not in valid_extensions:
                raise serializers.ValidationError("Unsupported file format. Please upload a JPEG or PNG image.")

            max_size = 2 * 1024 * 1024
            if value.size > max_size:
                raise serializers.ValidationError(
                    f"File too large. Size should not exceed {max_size // (1024 * 1024)}MB.")
        else:
            value = 'profile_pics/default_profilepic.jpg'
        return value


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = '__all__'


class StaffProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffProfile
        fields = '__all__'


class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminProfile
        fields = '__all__'

class UserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name')

class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    PROFILE_TYPE_MAP = {
        'student': (StudentProfile, StudentProfileSerializer),
        'staff': (StaffProfile, StaffProfileSerializer),
        'admin': (AdminProfile, StudentProfileSerializer),
    }

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'user_type', 'phone_number', 'profile')

    def get_profile(self, obj):
        user_type = obj.user_type.lower()
        if user_type not in self.PROFILE_TYPE_MAP:
            return None

        profile_class, serializer_class = self.PROFILE_TYPE_MAP[user_type]
        profile = profile_class.objects.filter(user=obj).first()

        return serializer_class(profile).data if profile else None

    def _create_profile(self, user, profile_data):
        if not profile_data:
            return

        serializer = self.get_profile(user)
        _, serializer_class = self.PROFILE_TYPE_MAP[user.user_type]
        profile = serializer_class(serializer, data=profile_data, partial=True)
        profile.is_valid(raise_exception=True)
        profile.save()

    def _update_user_fields(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.save()

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = User.objects.create_user(**validated_data)
        self._create_profile(user, profile_data)
        return user

    def update(self, instance, validated_data):
        profile_data = self.initial_data.get('profile')
        profile_class, serializer_class = self.PROFILE_TYPE_MAP[instance.user_type]
        self._update_user_fields(instance, validated_data)
        profile = profile_class.objects.filter(user=instance).first()
        updated = serializer_class(profile, data=profile_data, partial=True)
        updated.is_valid(raise_exception=True)
        updated.save()
        return instance


class CustomTokenObtainSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data.update({
            'user_id': user.id,
            'email': user.email,
            'user_type': user.user_type,
        })
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    user_type = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
