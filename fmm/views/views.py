from django.views.generic.base import TemplateView

from .functions import add_permissions_context_elements, add_useragent_context_elements


class IndexView(TemplateView):
  """
  view for main page

  :param template_name: template name
  """

  template_name = 'fmm/index.html'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add user agent related context elements
    context = add_useragent_context_elements(context, self.request)
    # add permissions related context elements
    context = add_permissions_context_elements(context, self.request.user)
    return context
