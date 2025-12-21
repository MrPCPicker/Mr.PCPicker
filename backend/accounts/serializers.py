from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password], 
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ('id', 'name', 'username', 'email', 'profile_image', 'password', 'password2')
        extra_kwargs = {
        'password': {'write_only': True},
        'password2': {'write_only': True},
        'name': {'required': True},
        'email': {'required': False},
        'profile_image': {'required': False}
    }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        # Remove password2 before creating user
        validated_data.pop('password2', None)
        password = validated_data.pop('password')
        user = User.objects.create_user(
            username=validated_data['username'],
            password=password,
            name=validated_data.get('name', '')
        )
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        # Check if username exists
        if not User.objects.filter(username=username).exists():
            raise serializers.ValidationError({
                'username': ['등록되지 않은 아이디입니다.']
            })
            
        # If username exists but password is wrong
        user = User.objects.get(username=username)
        if not user.check_password(password):
            raise serializers.ValidationError({
                'password': ['비밀번호가 틀렸습니다.']
            })
            
        # If credentials are valid, proceed with normal token creation
        data = super().validate(attrs)
        
        # Add custom claims
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'name': self.user.name or ''
        }
        
        return data

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    new_password2 = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        user = self.context['request'].user
        
        # Check if current password is correct
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError({
                'old_password': ['현재 비밀번호가 틀렸습니다.']
            })
            
        # Check if new passwords match
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                'new_password2': ['새 비밀번호가 일치하지 않습니다.']
            })
            
        return attrs

    def validate_new_password(self, value):
        try:
            # Remove the user parameter to disable similarity check with username/email
            validate_password(value)
        except ValidationError as e:
            # Filter out the similarity-related error
            filtered_errors = []
            for msg in e.messages:
                if "too similar" not in msg.lower() and "다른" not in msg:
                    filtered_errors.append(msg)
            if filtered_errors:
                # Log the specific validation error
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Password validation failed: {filtered_errors}")
                raise serializers.ValidationError(filtered_errors)
        return value

class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('name', 'username', 'email', 'profile_image')
        extra_kwargs = {
            'username': {'required': False},
            'name': {'required': False}
        }