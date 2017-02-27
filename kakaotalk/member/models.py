from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    name = models.CharField(max_length=50)
    img_profile = models.ImageField(upload_to='user', blank=True)
    access_token = models.CharField(max_length=50)
    refresh_token = models.CharField(max_length=50)

    def __str__(self):
        return self.name
