from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import UpdateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.core.mail import send_mail
from django_rest_passwordreset.models import ResetPasswordToken
from .models import CustomUser
from rest_framework_simplejwt.exceptions import TokenError
from .serializers import EmailLoginSerializer, UsernameRegisterSerializer, \
    ChangePasswordAccountSerializer, UpdateLoginSerializer, PhotoProfileSerializer
from .utils import send_account_confirmation_email, is_expired_decorator
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed


class UserRegistrationAPIView(APIView):
    """Registration class"""

    def post(self, request):
        """Processing registration form data and creating a new user"""
        serializer = UsernameRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = CustomUser.objects.create_user(username=username, email=email, password=password, is_active=False)

        """Send an account confirmation email"""
        send_account_confirmation_email(email, user.id)

        return Response({"user": serializer.data,
                         "message": "Registration was successful. Check your email to confirm your account."},
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
    """Custom class for login with email """

    def post(self, request):
        serializer = EmailLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            User = get_user_model()
            user = User.objects.filter(email=email).first()

            if user and user.check_password(password):
                refresh = RefreshToken.for_user(user)
                response_data = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'username': str(user.username),
                    'email': str(user.email),
                }

                if user.profile_photo:
                    response_data['profile_photo'] = user.profile_photo.url
                else:
                    response_data['profile_photo'] = "Photo doesnt not found"

                return Response(response_data)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RefreshUser(APIView):
    """ For reset page """

    def post(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response({'error': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh_token = RefreshToken(refresh_token)
            user_id = refresh_token['user_id']
            user = CustomUser.objects.get(pk=user_id)

            if user.profile_photo:
                profile_photo = user.profile_photo.url
            else:
                profile_photo = "Photo doesnt not found"

            return Response({'username': user.username, 'email': user.email, 'profile_photo': profile_photo})

        except TokenError:
            raise AuthenticationFailed('Invalid refresh token.', code='invalid_refresh_token')


class PasswordResetAPIView(APIView):
    """
       API view to handle the password reset request.

       This view sends a password reset email to the user's email address
       with a link containing a reset token.

   """

    def post(self, request):
        email = request.data.get('email')

        try:
            user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist:
            return Response({"message": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        reset_token = ResetPasswordToken.objects.create(user=user)

        reset_url = 'https://valerka4052.github.io/chat-talk-front/recover-password/?token=' + reset_token.key
        message = f'To reset your password, follow this link: {reset_url}'
        from_email = 'talk.team.challenge@gmail.com'
        to_email = email
        send_mail('Password Reset', message, from_email, [to_email])

        return Response({"message": "Password reset email has been sent. Check your email to reset your password."},
                        status=status.HTTP_200_OK)


@is_expired_decorator
class PasswordResetConfirmAPIView(APIView):
    """
        API view to handle the password reset confirmation.

        This view confirms the password reset by validating the reset token,
        updating the user's password, and deleting the used token.

    """

    def post(self, request):
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        try:
            reset_token = ResetPasswordToken.objects.get(key=token)

        except ResetPasswordToken.DoesNotExist:
            return Response({"message": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        if reset_token.is_expired():
            return Response({"message": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        user = reset_token.user
        user.set_password(new_password)
        user.save()

        reset_token.delete()

        return Response({"message": "Password has been reset successfully."}, status=status.HTTP_201_CREATED)



class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordAccountSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=self.request.user, data=request.data)
        serializer.is_valid(raise_exception=True)

        old_password = serializer.validated_data.get('old_password')

        if not self.request.user.check_password(old_password):
            return Response({"error": "Invalid old password."}, status=status.HTTP_400_BAD_REQUEST)

        self.request.user.set_password(serializer.validated_data['password'])
        self.request.user.save()

        return Response({"message": "Password has been changed successfully."}, status=status.HTTP_200_OK)



class UpdateProfilePhotoView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user_profile = CustomUser.objects.get(id=request.user.id)
        serializer = PhotoProfileSerializer(user_profile, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile photo has been updated successfully."}, status=200)
        else:
            return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile_photo(request, user_id):
    try:
        user_profile = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = PhotoProfileSerializer(user_profile)
    return Response(serializer.data)


class UpdateUserSettingsView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateLoginSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return Response({"message": "User settings have been updated successfully."}, status=status.HTTP_201_CREATED)


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        return Response({"message": "Account has been deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
