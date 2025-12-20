from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'accounts'

# DRF API endpoints
urlpatterns = [
    # JWT Authentication
    path('api/token/', views.LoginView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User management
    path('api/register/', views.SignupView.as_view(), name='register'),
    path('api/logout/', views.LogoutView.as_view(), name='logout'),
    
    # User profile
    path('api/user/', views.UserDetailView.as_view(), name='user_detail'),
    
    # Password management
    path('api/change-password/', views.ChangePasswordView.as_view(), name='change_password'),

    # Delete Account
    path('api/user/delete/', views.DeleteUserView.as_view(), name='user-delete'),

]
