from django.contrib.auth import get_user_model
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .serializers import (
    UserSerializer, 
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer,
    UpdateUserSerializer
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

User = get_user_model()

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

@permission_classes([AllowAny])
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # In a real implementation, you might want to blacklist the token
        return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)

@permission_classes([AllowAny])
class SignupView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate tokens for the new user
            refresh = RefreshToken.for_user(user)
            
            return Response({
                "message": "User created successfully",
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request):
        user = request.user
        serializer = UpdateUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "User updated successfully",
                "user": UserSerializer(user, context={'request': request}).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([AllowAny])
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 🔴 request를 context에 꼭 넣어준다
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        # 🔴 유효성 실패 시 자동으로 400 + 에러 메시지 리턴
        serializer.is_valid(raise_exception=True)

        # 🔴 검증 통과 후 실제 비밀번호 변경
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response(
            {"detail": "비밀번호가 성공적으로 변경되었습니다."},
            status=status.HTTP_200_OK
        )

class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        # Get user data before deletion (for response)
        user_data = UserSerializer(request.user).data
        
        # Log out the user by expiring their token
        from rest_framework_simplejwt.tokens import RefreshToken
        try:
            refresh_token = request.auth
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception as e:
            # Log the error but continue with account deletion
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error during token blacklisting: {str(e)}")
        
        # Delete the user account
        request.user.delete()
        
        # Clear the session
        request.session.flush()
        
        return Response(
            {
                "message": "Account deleted successfully and logged out",
                "user": user_data
            },
            status=status.HTTP_200_OK
        )
