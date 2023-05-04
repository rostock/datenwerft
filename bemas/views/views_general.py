from django.apps import apps
from django.conf import settings
from django.urls import reverse
from django.views.generic.base import TemplateView

from bemas.models import Codelist, Complaint, Originator
from .functions import add_default_context_elements, add_user_agent_context_elements, \
  get_model_objects


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


class MapView(TemplateView):
  """
  view for map page
  """

  template_name = 'bemas/map.html'

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
    # add map related information to context
    context['LEAFLET_CONFIG'] = settings.LEAFLET_CONFIG
    if (
        self.kwargs
        and 'model' in self.kwargs
        and self.kwargs['model']
        and 'subset_pk' in self.kwargs
        and self.kwargs['subset_pk']
    ):
      if self.kwargs['model'] == 'complaint':
        context['complaints_mapdata_url'] = reverse(
          'bemas:complaint_mapdata_subset', args=[self.kwargs['subset_pk']])
      elif self.kwargs['model'] == 'originator':
        context['originators_mapdata_url'] = reverse(
          'bemas:originator_mapdata_subset', args=[self.kwargs['subset_pk']])
    else:
      context['complaints_mapdata_url'] = reverse('bemas:complaint_mapdata')
      context['originators_mapdata_url'] = reverse('bemas:originator_mapdata')
    # add filter related information to context
    context['complaints_status'] = list(
      Complaint.objects.order_by('status').values_list('status__title', flat=True).distinct()
    )
    context['complaints_types_of_immission'] = list(
      Complaint.objects.order_by('type_of_immission').values_list(
        'type_of_immission__title', flat=True).distinct()
    )
    complaints_originators = Complaint.objects.order_by('originator').values_list(
      'originator', flat=True).distinct()
    complaints_originators_list = []
    for originator in complaints_originators:
      complaints_originators_list.append(
        Originator.objects.get(pk=originator).sector_and_operator())
    context['complaints_originators'] = complaints_originators_list
    context['originators_sectors'] = list(
      Originator.objects.order_by('sector').values_list('sector__title', flat=True).distinct()
    )
    context['originators_operators'] = list(
      Originator.objects.order_by('operator').values_list('operator__name', flat=True).distinct()
    )
    # add miscellaneous information to context
    context['objects_count'] = (
        get_model_objects(Complaint, True) + get_model_objects(Originator, True))
    context['complaints_color'] = settings.BEMAS_COLORS['complaint']
    context['originators_color'] = settings.BEMAS_COLORS['originator']
    return context
