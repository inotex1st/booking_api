from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

    def _str_(self):
        return self.username