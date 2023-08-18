from django.contrib.auth.models import User, AbstractUser
from django.db import models

from talk_app import settings


class CustomUser(AbstractUser):
    id = models.AutoField(primary_key=True)
    profile_photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)

    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"

