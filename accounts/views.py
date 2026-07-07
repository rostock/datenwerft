from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group, Permission, User
from django.contrib.auth.views import LoginView
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import viewsets

from angebotsdb.models.base import UserProfile
from angebotsdb.utils import is_angebotsdb_admin, is_angebotsdb_user

from d3.api import D3AuthenticationApi

from .emails import send_login_code
from .forms import ExternalAuthenticationForm
from .models import UserAuthToken
from .serializers import (
  ContentTypeSerializer,
  GroupSerializer,
  PermissionSerializer,
  UserSerializer,
)
from .utils import get_client_ip, ip_in_array


class PermissionViewSet(viewsets.ModelViewSet):
  queryset = Permission.objects.all()
  serializer_class = PermissionSerializer


class UserViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
  queryset = Group.objects.all()
  serializer_class = GroupSerializer


class ContentTypeViewSet(viewsets.ModelViewSet):
  queryset = ContentType.objects.all()
  serializer_class = ContentTypeSerializer
  # lookup_field = 'model'


class UserSettingsView(LoginRequiredMixin, View):
  """
  Nutzereinstellungen.
  - Allgemein: Passwort-Änderung für lokale Django-Nutzer (LDAP-Nutzer haben kein
    nutzbares Django-Passwort und sehen das Formular nicht)
  - Angebotsdatenbank: E-Mail-Benachrichtigungen, nur für AngebotsDB-Nutzer/-Admins
    sichtbar und änderbar (Opt-in, Standard: aus)
  """

  template_name = 'accounts/settings.html'

  @staticmethod
  def user_has_angebotsdb_access(user):
    """
    Prüft, ob der Nutzer die AngebotsDB-Einstellungen sehen darf
    (Muster: angebotsdb.views.functions.add_permission_context_elements).

    :param user: Django-User-Instanz
    :return: Nutzer ist AngebotsDB-Nutzer, -Admin oder Superuser?
    """
    return user.is_superuser or is_angebotsdb_user(user) or is_angebotsdb_admin(user)

  def get_context(self, request, password_form=None):
    """
    Baut den Template-Kontext für die Einstellungs-Seite.

    :param request: request
    :param password_form: gebundenes PasswordChangeForm mit Fehlern (nach invalidem POST)
    :return: Kontext-Dictionary
    """
    context = {'is_angebotsdb_user': self.user_has_angebotsdb_access(request.user)}
    if context['is_angebotsdb_user']:
      profile = UserProfile.objects.filter(user_id=request.user.id).first()
      context['receive_email_notifications'] = bool(
        profile and profile.receive_email_notifications
      )
    if request.user.has_usable_password():
      context['password_form'] = password_form or PasswordChangeForm(user=request.user)
    return context

  def get(self, request):
    return render(request, self.template_name, self.get_context(request))

  def post(self, request):
    if 'change_password' in request.POST:
      return self.handle_password_change(request)
    return self.handle_notifications(request)

  def handle_password_change(self, request):
    """
    Ändert das Passwort eines lokalen Django-Nutzers direkt auf der Einstellungs-Seite.
    """
    if not request.user.has_usable_password():
      raise PermissionDenied
    password_form = PasswordChangeForm(user=request.user, data=request.POST)
    if password_form.is_valid():
      user = password_form.save()
      # Session-Hash aktualisieren, damit der Nutzer eingeloggt bleibt
      update_session_auth_hash(request, user)
      messages.success(request, 'Ihr Passwort wurde geändert.')
      return redirect('accounts:settings')
    return render(request, self.template_name, self.get_context(request, password_form))

  def handle_notifications(self, request):
    """
    Speichert die AngebotsDB-Benachrichtigungseinstellung.
    """
    if not self.user_has_angebotsdb_access(request.user):
      raise PermissionDenied
    profile, _ = UserProfile.objects.get_or_create(user_id=request.user.id)
    profile.receive_email_notifications = bool(request.POST.get('receive_email_notifications'))
    profile.save(update_fields=['receive_email_notifications'])
    messages.success(request, 'Einstellungen gespeichert.')
    return redirect('accounts:settings')


class PreLoginView(LoginView):
  """
  Login View
  users with internal ip address go through the normal login process.
  Users with external IP address have to go through a two-factor authentication process
  """

  template_name = 'accounts/login.html'
  redirect_authenticated_user = True

  def form_valid(self, form):
    """Security check complete. Log the user in."""
    user = form.get_user()
    user_ip = get_client_ip(self.request)
    if ip_in_array(user_ip, settings.AUTH_LDAP_EXTENSION_INTERNAL_IP_ADDRESSES):
      # user is internal
      login(self.request, user)
      try:
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        authentication_api = D3AuthenticationApi()
        self.request.session['d3_login'] = authentication_api.lade_access_token(username, password)
      except Exception:
        pass
      return HttpResponseRedirect(self.get_success_url())
    else:
      # user is external next step is to generate login tokens
      user_auth, create = UserAuthToken.objects.get_or_create(user=user)
      if not create:
        # refresh tokens
        user_auth.save()
      user_auth.refresh_from_db()
      self.request.session['_token'] = f'{user_auth.session_token}'
      send_login_code(user_auth.user)
      # url_token is only to show a dynamic url.
      # The crucial token is the session token
      return HttpResponseRedirect(
        reverse('accounts:external_login', kwargs={'url_token': user_auth.url_token})
      )


class ExternalLoginView(LoginView):
  """
  second login View for external user
  """

  template_name = 'accounts/login_add_token.html'
  form_class = ExternalAuthenticationForm
  redirect_authenticated_user = True

  @method_decorator(sensitive_post_parameters('email_token'))
  @method_decorator(csrf_protect)
  def dispatch(self, request, *args, **kwargs):
    session_token = request.session.get('_token')
    url_token = kwargs.get('url_token')
    if not session_token or not url_token:
      # something wrong, restart login process
      return HttpResponseRedirect(reverse('accounts:login'))
    try:
      UserAuthToken.objects.get(session_token=session_token, url_token=url_token)
    except UserAuthToken.DoesNotExist:
      if session_token:
        request.session.pop('_token')
      raise Http404()
    else:
      user_ip = get_client_ip(self.request)
      if ip_in_array(user_ip, settings.AUTH_LDAP_EXTENSION_INTERNAL_IP_ADDRESSES):
        # user is internal
        # the token is not needed
        request.session.pop('_token')
        return HttpResponseRedirect(reverse('accounts:login'))
    return super().dispatch(request, *args, **kwargs)
