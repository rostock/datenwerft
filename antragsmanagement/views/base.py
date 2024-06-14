from django.contrib.messages import success
from django.forms.models import modelform_factory
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView

from .forms import GenericObjectForm
from .functions import add_model_context_elements, add_useragent_context_elements, assign_widget


class GenericObjectFormMixin:
  """
  generic mixin for form page for creating or updating an instance of a general object
  """

  template_name = 'antragsmanagement/simple-form.html'
  model = None
  success_message = ''

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

  def form_valid(self, form):
    """
    sends HTTP response if passed form is valid

    :param form: form
    :return: HTTP response if passed form is valid
    """
    success(
      self.request,
      self.success_message.format(self.model._meta.verbose_name, str(form.instance))
    )
    return super().form_valid(form)

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add user agent related context elements
    context = add_useragent_context_elements(context, self.request)
    # add model related context elements
    context = add_model_context_elements(context, self.model)
    context['cancel_url'] = reverse('antragsmanagement:index')
    return context


class GenericObjectCreateView(GenericObjectFormMixin, CreateView):
    success_message = '{} <strong><em>{}</em></strong> erfolgreich neu angelegt!'


class GenericObjectUpdateView(GenericObjectFormMixin, UpdateView):
    success_message = '{} <strong><em>{}</em></strong> erfolgreich geändert!'
