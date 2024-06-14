from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView

from .base import GenericObjectUpdateView
from .functions import add_permissions_context_elements, add_useragent_context_elements
from antragsmanagement.models import Authority, Email


#
# general
#

class IndexView(TemplateView):
  """
  view for main page
  """

  template_name = 'antragsmanagement/index.html'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    context = add_useragent_context_elements(context, self.request)
    context = add_permissions_context_elements(context, self.request.user)
    context['cancel_url'] = '#'
    return context


#
# general objects
#

class AuthorityUpdateView(GenericObjectUpdateView):
  """
  view for form page for updating an instance of general object:
  authority (Behörde)
  """

  model = Authority


class EmailUpdateView(GenericObjectUpdateView):
  """
  view for form page for updating an instance of general object:
  email (E-Mail)
  """

  model = Email
