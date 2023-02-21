from django.views.generic.base import TemplateView

from bemas.utils import is_bemas_admin, is_bemas_user


class IndexView(TemplateView):
  """
  main page view
  """

  template_name = 'bemas/index.html'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    if self.request.user.is_superuser or is_bemas_user(self.request.user):
      context['is_bemas_user'] = True
    else:
      context['is_bemas_user'] = False
    context['is_bemas_admin'] = is_bemas_admin(self.request.user)
    return context
