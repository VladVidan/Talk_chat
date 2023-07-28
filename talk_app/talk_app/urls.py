"""
URL configuration for talk_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
# from talk_core.views import EmailLoginAPIView, UserRegistrationAPIView, confirm_account

from  talk_core.views import EmailLoginAPIView, UserRegistrationAPIView , confirm_account , PasswordResetAPIView , PasswordResetConfirmAPIView


urlpatterns = [
    path('api/v1/admin/', admin.site.urls),
    path('api/v1/login/', EmailLoginAPIView.as_view(), name='email-login'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/register/', UserRegistrationAPIView.as_view(), name='user-registration'),
    path('confirm/<int:user_id>/', confirm_account, name='confirm-account'),
    path('api/v1/password_reset/', PasswordResetAPIView.as_view(), name='password-reset'),
    path('api/v1/password_reset_confirm/', PasswordResetConfirmAPIView.as_view(), name='password-reset-confirm'),
]