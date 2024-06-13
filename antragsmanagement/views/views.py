from django.conf import settings
from django.forms.models import modelform_factory
from django.urls import reverse
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView

from .forms import GenericObjectForm
from .functions import add_model_context_elements, add_permissions_context_elements, \
  add_useragent_context_elements, assign_widget
from antragsmanagement.models import Authority


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

class AuthorityUpdateView(UpdateView):
  """
  view for form page for updating an instance of general object:
  authority (Behörde)
  """

  template_name = 'antragsmanagement/simple-form.html'

  def __init__(self, model=Authority, *args, **kwargs):
    self.model = model
    self.form_class = modelform_factory(
      self.model,
      form=GenericObjectForm,
      fields='__all__',
      formfield_callback=assign_widget
    )
    super().__init__(*args, **kwargs)

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    context = add_useragent_context_elements(context, self.request)
    context = add_permissions_context_elements(
      context, self.request.user, settings.ANTRAGSMANAGEMENT_ADMIN_GROUP_NAME)
    context = add_model_context_elements(context, self.model)
    context['cancel_url'] = reverse('antragsmanagement:index')
    return context
