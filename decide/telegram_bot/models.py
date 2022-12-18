from django.db import models

# Create your models here.

class TelegramSubscription(models.Model):
    chat_id = models.IntegerField()
    voting_id = models.IntegerField()