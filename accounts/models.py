from django.db import models

# Create your models here.
class user_info(models.Model):
    unit = models.CharField(max_length=255)