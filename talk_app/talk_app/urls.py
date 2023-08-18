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
from django.contrib.auth.views import LogoutView
from django.urls import path
from talk_app.yasg import urlpatterns as doc_urls
from rest_framework_simplejwt.views import TokenRefreshView
from talk_core.views import EmailLoginAPIView, UserRegistrationAPIView, confirm_account, PasswordResetAPIView, \
    PasswordResetConfirmAPIView, RefreshUser, ChangePasswordView, UpdateUserSettingsView

urlpatterns = [
    path('api/v1/admin/', admin.site.urls),
    path('api/v1/login/', EmailLoginAPIView.as_view(), name='email-login'),
    path('api/v1/logout/', LogoutView.as_view(), name='logout'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/register/', UserRegistrationAPIView.as_view(), name='user-registration'),
    path('api/v1/confirm/<int:user_id>/', confirm_account, name='confirm-account'),
    path('api/v1/password_reset/', PasswordResetAPIView.as_view(), name='password-reset'),
    path('api/v1/password_reset_confirm/', PasswordResetConfirmAPIView.as_view(), name='password-reset-confirm'),
    path('api/v1/refresh_user/', RefreshUser.as_view(), name='refresh-user'),
    path('api/v1/change_password/<int:pk>/',  ChangePasswordView.as_view(), name='change_password'),
    path('api/v1/update_user_settings/', UpdateUserSettingsView.as_view(), name='update-user-settings'),
]

urlpatterns += doc_urls
