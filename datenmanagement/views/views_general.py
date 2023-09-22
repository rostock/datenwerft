from django.apps import apps
from django.views.generic.base import TemplateView

from datenmanagement.models.base import Codelist, ComplexModel, Metamodel
from datenmanagement.utils import user_has_model_permissions_at_all


class IndexView(TemplateView):
  """
  view for main page
  """

  template_name = 'datenmanagement/index.html'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    models_meta, models_codelist, models_complex, models_simple = [], [], [], []
    models = apps.get_app_config('datenmanagement').get_models()
    for model in models:
      if user_has_model_permissions_at_all(self.request.user, model):
        model_dict = {
          'name': model.__name__,
          'verbose_name_plural': model._meta.verbose_name_plural,
          'description': model.BasemodelMeta.description
        }
        if issubclass(model, Metamodel):
          models_meta.append(model_dict)
        elif issubclass(model, Codelist):
          models_codelist.append(model_dict)
        elif issubclass(model, ComplexModel):
          models_complex.append(model_dict)
        else:
          models_simple.append(model_dict)
    context = super().get_context_data(**kwargs)
    context['models_meta'] = models_meta
    context['models_codelist'] = models_codelist
    context['models_complex'] = models_complex
    context['models_simple'] = models_simple
    return context


class StartView(TemplateView):
  """
  view for entry page of a model

  :param model: model
  """

  model = None
  template_name = 'datenmanagement/start.html'

  def __init__(self, model=None):
    self.model = model
    super().__init__()

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    context['model_name'] = self.model.__name__
    context['model_name_lower'] = self.model.__name__.lower()
    context['model_verbose_name_plural'] = self.model._meta.verbose_name_plural
    context['model_description'] = self.model.BasemodelMeta.description
    context['model_is_editable'] = self.model.BasemodelMeta.editable
    context['model_has_geometry'] = self.model.BasemodelMeta.geometry_type
    return context
