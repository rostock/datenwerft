from django.conf import settings
from django.forms.models import modelform_factory
from django.urls import reverse
from django.views.generic.edit import UpdateView

from .forms import GenericObjectForm
from .functions import add_model_context_elements, add_permissions_context_elements, \
  add_useragent_context_elements, assign_widget


class GenericObjectUpdateView(UpdateView):
  """
  generic view for form page for updating an instance of a general object
  """

  template_name = 'antragsmanagement/simple-form.html'
  model = None

  def get_form_class(self):
    # ensure the model is set before creating the form class
    if not self.model:
     raise ValueError('The model attribute must be set before calling get_form_class.')
    # dynamically create the form class
    form_class = modelform_factory(
      self.model,
      form=GenericObjectForm,
      fields='__all__',
      formfield_callback=assign_widget
    )
    return form_class

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
