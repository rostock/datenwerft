from django.shortcuts import redirect
from django.views.generic.base import TemplateView

from bemas.utils import is_bemas_user


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
    if (
        request.user.is_authenticated
        and not request.user.is_superuser
        and not is_bemas_user(request.user)
    ):
      return redirect('datenmanagement:index')
    elif (
        request.user.is_authenticated
        and is_bemas_user(request.user, only_bemas_user_check=True)
    ):
      return redirect('bemas:index')
    else:
      return super(IndexView, self).dispatch(request, *args, **kwargs)
