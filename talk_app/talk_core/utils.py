from datetime import timedelta

from django.shortcuts import redirect
from django_rest_passwordreset.models import ResetPasswordToken
from django.core.mail import send_mail
from django.utils import timezone
from talk_app import settings


def is_expired_decorator(cls):
    """
        Decorator to add an 'is_expired' method to the class.

        This method checks if the token is expired based on its creation time.

    """
    def is_expired(self):
        expiration_time = self.created_at + timedelta(hours=1)
        return timezone.now() > expiration_time

    cls.is_expired = is_expired
    return cls
ResetPasswordToken = is_expired_decorator(ResetPasswordToken)



def send_account_confirmation_email(email, user_id):
    subject = 'Account Confirmation'
    message = f'To confirm your account, follow this link: {settings.API_HOST}/api/v1/confirm/{user_id}/'
    from_email = 'talk.team.challenge@gmail.com'
    to_email = email
    send_mail(subject, message, from_email, [to_email])

