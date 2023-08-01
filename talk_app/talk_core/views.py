from typing import Generic

from django.contrib.auth import get_user_model
from django_rest_passwordreset.models import ResetPasswordToken
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenViewBase, TokenRefreshView

from .models import CustomResetPasswordToken
from .serializers import EmailLoginSerializer
from django.shortcuts import redirect


class UserRegistrationAPIView(APIView):
    """Registration class"""

    def post(self, request):
        """"Processing registration form data and creating a new user"""

        username = request.data.get('email')
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.create_user(username=username, email=email, password=password, is_active=False)

        """Send an account confirmation email"""
        subject = 'Account Confirmation'
        message = f'To confirm your account, follow this link: http://talk.pythonanywhere.com/api/v1/confirm/{user.id}/'
        from_email = 'talk.team.challenge@gmail.com'
        to_email = email
        send_mail(subject, message, from_email, [to_email])

        return Response({"message": "Registration was successful. Check your email to confirm your account.."},
                        status=status.HTTP_201_CREATED)


@api_view(['GET'])
def confirm_account(request, user_id):
    User = get_user_model()

    try:
        user = User.objects.get(pk=user_id)
        if not user.is_active:
            user.is_active = True
            user.save()

            return redirect('https://valerka4052.github.io/chat-talk-front/login/')
        else:
            return Response({"message": "The account has already been confirmed previously."},
                            status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({"message": "Account not found."}, status=status.HTTP_404_NOT_FOUND)


class EmailLoginAPIView(APIView):
    """Custom class for login with email"""

    def post(self, request):
        serializer = EmailLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            User = get_user_model()
            user = User.objects.filter(email=email).first()

            if user and user.check_password(password):
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'username': str(user.username)
                })
            else:
                return Response({'error': 'Неверные учетные данные'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')

        try:
            user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist:
            return Response({"message": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        reset_token = CustomResetPasswordToken.objects.create(user=user)

        reset_url = 'https://valerka4052.github.io/chat-talk-front/recover-password/?token=' + reset_token.key
        message = f'To reset your password, follow this link: {reset_url}'
        from_email = 'talk.team.challenge@gmail.com'
        to_email = email
        send_mail('Password Reset', message, from_email, [to_email])

        return Response({"message": "Password reset email has been sent. Check your email to reset your password."},
                        status=status.HTTP_200_OK)


class PasswordResetConfirmAPIView(APIView):
    def post(self, request):
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        try:
            reset_token = CustomResetPasswordToken.objects.get(key=token)


        except  CustomResetPasswordToken.DoesNotExist:
            return Response({"message": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        if reset_token.is_expired():
            return Response({"message": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        user = reset_token.user
        user.set_password(new_password)
        user.save()

        reset_token.delete()

        return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)


