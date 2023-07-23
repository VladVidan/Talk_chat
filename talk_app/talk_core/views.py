from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail

from django.contrib.auth.models import User
<<<<<<< HEAD
from rest_framework_simplejwt.tokens import RefreshToken

from talk_core.serializers import EmailLoginSerializer
=======
from rest_framework_simplejwt.views import TokenObtainPairView
>>>>>>> 169a813498d18dde62a79b781273106edd9d0842


class UserRegistrationAPIView(APIView):
    """Registration class"""
    def post(self, request):
        """"Processing registration form data and creating a new user"""
<<<<<<< HEAD
=======
        # username = request.data.get('email')
>>>>>>> 169a813498d18dde62a79b781273106edd9d0842
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.create_user(username=email, email=email, password=password, is_active=False)

        """Send an account confirmation email"""
        subject = 'Account Confirmation'
        message = f'To confirm your account, follow this link: http://127.0.0.1:8000/confirm/{user.id}/'
        from_email = 'talk.team.challenge@gmail.com'
        to_email = email
        send_mail(subject, message, from_email, [to_email])

        return Response({"message": "Registration was successful. Check your email to confirm your account.."},
                        status=status.HTTP_201_CREATED)


@api_view(['GET'])
def confirm_account(request, user_id):
    _user = get_user_model()

    try:
        user = _user.objects.get(pk=user_id)
        if not user.is_active:
            user.is_active = True
            user.save()
            return Response({"message": "Account successfully confirmed."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "The account has already been confirmed previously."}, status=status.HTTP_400_BAD_REQUEST)
    except _user.DoesNotExist:
        return Response({"message": "Account not found."}, status=status.HTTP_404_NOT_FOUND)


class EmailLoginView(APIView):
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
                })
            else:
                return Response({'error': 'Неверные учетные данные'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)