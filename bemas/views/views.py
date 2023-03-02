from django.apps import apps
from django.contrib.messages import success
from django.forms.models import modelform_factory
from django.views.generic import CreateView
from django.views.generic.base import TemplateView

from .forms import CodelistForm
from .functions import add_default_context_elements, add_user_agent_context_elements, assign_widget


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
    # add default elements to context
    context = add_default_context_elements(context, self.request.user)
    return context


class CodelistsIndexView(TemplateView):
  """
  codelists entry page view
  """

  template_name = 'bemas/codelists.html'

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
    context = add_user_agent_context_elements(context, self.request.user_agent)
    # add list of codelists to context
    codelists = []
    models = apps.get_app_config('bemas').get_models()
    for model in models:
        codelist = {
          'name': model.__name__,
          'verbose_name_plural': model._meta.verbose_name_plural,
          'description': model._meta.description
        }
        if hasattr(model._meta, 'codelist') and model._meta.codelist is True:
          codelists.append(codelist)
    context['codelists'] = codelists
    return context


class CodelistIndexView(TemplateView):
  """
  entry page for a codelist view

  :param model: codelist model
  """

  model = None
  template_name = 'bemas/codelist.html'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add default elements to context
    context = add_default_context_elements(context, self.request.user)
    # add other necessary elements to context
    context['codelist_name'] = self.model.__name__
    context['codelist_verbose_name_plural'] = self.model._meta.verbose_name_plural
    context['codelist_description'] = self.model._meta.description
    return context


class CodelistCreateView(CreateView):
  """
  form page for creating a codelist view
  """

  template_name = 'bemas/codelist-form.html'

  def __init__(self, model=None, *args, **kwargs):
    self.model = model
    self.form_class = modelform_factory(
      self.model,
      form=CodelistForm,
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
    # add other necessary elements to context
    context['codelist_name'] = self.model.__name__
    context['codelist_verbose_name'] = self.model._meta.verbose_name
    return context

  def form_valid(self, form):
    """
    sends HTTP response if given form is valid

    :param form: form
    :return: HTTP response if given form is valid
    """
    success(
      self.request,
      'Der neue Codelisteneintrag <strong><em>%s</em></strong> '
      'wurde erfolgreich angelegt!' % str(form.instance)
    )
    return super().form_valid(form)
