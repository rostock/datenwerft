from django.conf import settings
from django.core.cache import cache
from django_auth_ldap.backend import LDAPBackend, _LDAPConfig, _LDAPUser

from .utils import get_client_ip

logger = _LDAPConfig.get_logger()


class DatenwerkAuthBackend(LDAPBackend):
  default_settings = {
    "LOGIN_COUNTER_KEY": "CUSTOM_LDAP_LOGIN_ATTEMPT_COUNT",
    "LOGIN_ATTEMPT_LIMIT": 3,
    "PERMIT_EMPTY_PASSWORD": False,
    "RESET_TIME": 30 * 60,
  }

  def authenticate(self, request, username=None, password=None, **kwargs):
    if username is None:
      return None

    if password or self.settings.PERMIT_EMPTY_PASSWORD:
      ldap_user = _LDAPUser(self, username=username.strip(), request=request)
      user_ip = get_client_ip(request)
      if user_ip not in settings.AUTH_LDAP_EXTENSION_INTERNAL_IP_ADDRESSES:
        user = self.external_authenticate(ldap_user, password)
      else:
        user = self.authenticate_ldap_user(ldap_user, password)
    else:
      logger.debug("Rejecting empty password for %s", username)
      user = None

    return user

  def external_authenticate(self, ldap_user, password):
    # When the user logs in from external.
    # Let's limit the number of login attempts.
    if self.exceeded_login_attempt_limit():
      # Or you can raise a 403 if you do not want
      # to continue checking other auth backends
      logger.debug("Login attempts exceeded. %s", ldap_user)
      return None
    self.increment_login_attempt_count()
    user = ldap_user.authenticate(password)
    # now the user is written into the session.
    # But the user is not logged in yet.
    # more logic can be implemented here: e.g.
    #   if user and user.email:
    #      self.send_email(user)
    return user

  @property
  def login_attempt_count(self):
    return cache.get_or_set(
      self.settings.LOGIN_COUNTER_KEY, 0, self.settings.RESET_TIME
    )

  def increment_login_attempt_count(self):
    try:
      cache.incr(self.settings.LOGIN_COUNTER_KEY)
    except ValueError:
      cache.set(self.settings.LOGIN_COUNTER_KEY, 1, self.settings.RESET_TIME)

  def exceeded_login_attempt_limit(self):
    return self.login_attempt_count >= self.settings.LOGIN_ATTEMPT_LIMIT
