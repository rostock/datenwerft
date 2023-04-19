from django.apps import apps
from django.urls import reverse
from django.views.generic.base import TemplateView

from bemas.models import Codelist
from .functions import add_default_context_elements


class IndexView(TemplateView):
  """
  view for main page
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
  view for codelists entry page
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
    # add list of codelists to context
    codelists = []
    models = apps.get_app_config('bemas').get_models()
    for model in models:
      if issubclass(model, Codelist):
        codelists.append({
          'table_url': reverse('bemas:codelists_' + model.__name__.lower() + '_table'),
          'verbose_name_plural': model._meta.verbose_name_plural,
          'description': model.BasemodelMeta.description
        })
    context['codelists'] = codelists
    return context
