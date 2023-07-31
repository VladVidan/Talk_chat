from django.db import models
from django.db import models
from django.utils import timezone
from datetime import timedelta
# Create your models here.
from django_rest_passwordreset.models import ResetPasswordToken


class CustomResetPasswordToken(ResetPasswordToken):
    def is_expired(self):
        expiration_time = self.created_at + timedelta(hours=1)
        return timezone.now() > expiration_time
