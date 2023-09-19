import binascii
import os

from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from zoneinfo import ZoneInfo

from .utils import generate_key


class UserAuthToken(models.Model):
  """
  Tokens storage
  When user is trying to login from an external network, we use tow-factor authentication.
  """

  user = models.OneToOneField(
    User,
    primary_key=True,
    on_delete=models.CASCADE
  )
  session_token = models.CharField(
    max_length=40,
    unique=True
  )
  url_token = models.CharField(
    max_length=24,
    unique=True
  )
  email_token = models.CharField(max_length=16)
  created_at = models.DateTimeField(
    auto_now=True,
    editable=False,
  )

  @classmethod
  def generate_session_token(cls):
    token = binascii.hexlify(os.urandom(20)).decode()
    if cls.objects.filter(session_token=token).exists():
      cls.generate_session_token()
    return token

  def is_expired_token(self):
    live_time = getattr(settings, "AUTH_LDAP_EXTENSION_ACCESS_TOKEN_LIFETIME", 5 * 60)
    local_tz = ZoneInfo(settings.TIME_ZONE)
    max_age = self.created_at.astimezone(local_tz) + timedelta(seconds=live_time)
    return datetime.now().astimezone(local_tz) >= max_age

  def save(self, *args, **kwargs):
    self.session_token = self.generate_session_token()
    self.email_token = generate_key()
    self.url_token = generate_key(codelength=20)
    super().save(*args, **kwargs)

  class Meta:
    verbose_name = "AuthToken"
    verbose_name_plural = "AuthTokens"

  def __str__(self):
    return f"{self.user} {self.created_at}"
