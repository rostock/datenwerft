from django.conf import settings
from django.urls import reverse, NoReverseMatch


def address_search_key(request):
  """
  holt den API-Key für die Adressensuche aus den Einstellungen

  :param request: Anfrage
  :return: API-Key für die Adressensuche
  """
  return {'address_search_key': settings.ADDRESS_SEARCH_KEY}


def datenwerft_version(request):
  """
  holt die Versionsnummer der Anwendung aus den Einstellungen

  :param request: Anfrage
  :return: Versionsnummer der Anwendung
  """
  return {'datenwerft_version': settings.DATENWERFT_VERSION}


def include_login_form(request):
  """
  setzt das Login-Formular

  :param request: Anfrage
  :return: Login-Formular
  """
  from django.contrib.auth.forms import AuthenticationForm
  form = AuthenticationForm()
  loginredirect = request.get_full_path()
  try:
    if request.get_full_path() == reverse('logout'):
      loginredirect = reverse('events:list')
  except NoReverseMatch:
    loginredirect = request.get_full_path()
  return {
    'login_form': form,
    'current_path': loginredirect
  }
