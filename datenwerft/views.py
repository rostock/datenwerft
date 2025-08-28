from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView

from antragsmanagement.utils import is_antragsmanagement_user
from bemas.utils import is_bemas_user
from fmm.utils import is_fmm_user


class IndexView(TemplateView):
  """
  main page view
  """

  template_name = 'index.html'

  def dispatch(self, request, *args, **kwargs):
    """
    renders main page or redirects to one of the app main pages instead

    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    if request.user.is_authenticated:
      if (
        not request.user.is_superuser
        and not request.user.is_staff
        and not is_antragsmanagement_user(request.user)
        and not is_bemas_user(request.user)
        and not is_fmm_user(request.user)
      ):
        return redirect('datenmanagement:index')
      elif is_antragsmanagement_user(request.user, only_antragsmanagement_user_check=True):
        return redirect('antragsmanagement:index')
      elif is_bemas_user(request.user, only_bemas_user_check=True):
        return redirect('bemas:index')
      elif is_fmm_user(request.user, only_fmm_user_check=True):
        return redirect('fmm:index')

    return super(IndexView, self).dispatch(request, *args, **kwargs)


def error_400(request, exception=None):
  context = {
    'error_code': '400',
    'error_text': 'Bad request',
    'error_message': 'Die Anfrage kann nicht bearbeitet werden, da sie fehlerhaft war '
    '(fehlerhafte Syntax und/oder unbekannte Zeichen in der Anfrage).',
  }
  return render(request, 'error.html', context)


def error_403(request, exception=None):
  context = {
    'error_code': '403',
    'error_text': 'Forbidden',
    'error_message': 'Sie dürfen auf die von Ihnen angefragte Ressource nicht zugreifen.',
  }
  return render(request, 'error.html', context)


def error_404(request, exception=None):
  context = {
    'error_code': '404',
    'error_text': 'Not found',
    'error_message': 'Die von Ihnen angefragte Ressource ist nicht vorhanden. '
    'Bitte überprüfen Sie die Schreibweise der Anforderung '
    '(vorallem Groß- und Kleinschreibung), Ihr Lesezeichen und/oder '
    'die Seite, von der Sie gekommen sind.',
  }
  return render(request, 'error.html', context)


def error_405(request, exception=None):
  context = {
    'error_code': '405',
    'error_text': 'Method not allowed',
    'error_message': 'Die Anforderungsmethode ist dem Server zwar bekannt ist, '
    'wird aber von der Zielressource nicht unterstützt.',
  }
  return render(request, 'error.html', context)


def error_410(request, exception=None):
  context = {
    'error_code': '410',
    'error_text': 'Gone',
    'error_message': 'Die von Ihnen angefragte Ressource existiert nicht mehr '
    'und es ist keine Weiterleitung bekannt.',
  }
  return render(request, 'error.html', context)


def error_500(request, exception=None):
  context = {
    'error_code': '500',
    'error_text': 'Internal server error',
    'error_message': 'Die Anfrage kann nicht bearbeitet werden, '
    'da auf dem Server ein unerwarteter Fehler aufgetreten ist. '
    'Bitte versuchen Sie es zu einem späteren Zeitpunkt wieder.',
  }
  return render(request, 'error.html', context)


def error_501(request, exception=None):
  context = {
    'error_code': '501',
    'error_text': 'Not implemented',
    'error_message': 'Die Anfrage kann nicht bearbeitet werden, '
    'da der Server nicht über die hierfür nötige Funktionalität verfügt.',
  }
  return render(request, 'error.html', context)


def error_502(request, exception=None):
  context = {
    'error_code': '502',
    'error_text': 'Bad gateway',
    'error_message': 'Der Server, in diesem Fall ein Proxy, kann die Anfrage nicht ausführen, '
    'weil im weiteren Verlauf ein Fehler aufgetreten ist. '
    'Bitte versuchen Sie es zu einem späteren Zeitpunkt wieder.',
  }
  return render(request, 'error.html', context)


def error_503(request, exception=None):
  context = {
    'error_code': '503',
    'error_text': 'Service unavailable',
    'error_message': 'Die Anfrage kann auf Grund von Server-Überlastungen, -Ausfällen '
    'oder -Wartungsarbeiten zur Zeit nicht bearbeitet werden. '
    'Bitte versuchen Sie es zu einem späteren Zeitpunkt wieder.',
  }
  return render(request, 'error.html', context)
