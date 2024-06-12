from django.forms.models import modelform_factory
from django.views.generic.edit import UpdateView

from .forms import GenericObjectForm
from .functions import add_default_context_elements, add_user_agent_context_elements, assign_widget
from antragsmanagement.models import Authority


#
# general objects
#

class AuthorityUpdateView(UpdateView):
  """
  view for form page for updating an instance of general object:
  authority (Behörde)
  """

  template_name = 'antragsmanagement/generic-object-form.html'

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
    # add default elements to context
    context = add_default_context_elements(context, self.request.user)
    # add user agent related elements to context
    context = add_user_agent_context_elements(context, self.request)
    # add other necessary elements to context
    context = add_generic_objectclass_context_elements(context, model)
    context['cancel_url'] = '#'
    return context