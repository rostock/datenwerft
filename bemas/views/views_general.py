from datetime import timedelta
from django.apps import apps
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.views.generic.base import TemplateView

from bemas.models import Codelist, Complaint, Contact, Organization, Originator, Person, Status
from bemas.utils import get_complaint_status_change_deadline_date, get_orphaned_organizations, \
  get_orphaned_originators, get_orphaned_persons
from .functions import add_default_context_elements, add_user_agent_context_elements, \
  format_date_datetime, get_lastest_activity_objects, get_model_objects


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
    # add user agent related elements to context
    context = add_user_agent_context_elements(context, self.request)
    # add latest activity objects to context
    context['lastest_activity_objects'] = get_lastest_activity_objects(5)
    # add statistics to context
    num_complaints = Complaint.objects.all().count()
    one_year_ago = (timezone.now() - timedelta(days=365)).date()
    one_year_ago_formatted = format_date_datetime(one_year_ago)
    one_month_ago = (timezone.now() - timedelta(days=30)).date()
    one_month_ago_formatted = format_date_datetime(one_month_ago)
    statistics = []
    # total complaints by type of immission
    still_in_progress = Complaint.objects.filter(status__ordinal__lt=2).count()
    statistics.append({
      'text': 'Gesamtzahl Beschwerden:',
      'figure': '{} (davon {} noch in Bearbeitung)'.format(num_complaints, still_in_progress)
    })
    # complaints received during last year
    complaints = Complaint.objects.filter(date_of_receipt__gte=one_year_ago)
    total = complaints.count()
    still_in_progress = complaints.filter(status__ordinal__lt=2).count()
    statistics.append({
      'text': 'im letzten Jahr (seit {}) eingegangene Beschwerden:'.format(
        one_year_ago_formatted),
      'figure': '{} (davon {} noch in Bearbeitung)'.format(total, still_in_progress)
    })
    # complaints received during last month
    complaints = Complaint.objects.filter(date_of_receipt__gte=one_month_ago)
    total = complaints.count()
    still_in_progress = complaints.filter(status__ordinal__lt=2).count()
    statistics.append({
      'text': 'in den letzten 30 Tagen (seit {}) eingegangene Beschwerden:'.format(
        one_month_ago_formatted),
      'figure': '{} (davon {} noch in Bearbeitung)'.format(total, still_in_progress)
    })
    # complaints closed during last year (and still closed)
    figure = Complaint.objects.filter(status=Status.get_closed_status()).filter(
      status_updated_at__gte=one_year_ago).count()
    statistics.append({
      'text': 'im letzten Jahr (seit {}) abgeschlossene Beschwerden:'.format(
        one_year_ago_formatted),
      'figure': figure
    })
    # complaints closed during last month (and still closed)
    figure = Complaint.objects.filter(status=Status.get_closed_status()).filter(
      status_updated_at__gte=one_month_ago).count()
    statistics.append({
      'text': 'in den letzten 30 Tagen (seit {}) abgeschlossene Beschwerden:'.format(
        one_month_ago_formatted),
      'figure': figure
    })
    if num_complaints:
      context['statistics'] = statistics
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


class OrphanedDataView(TemplateView):
  """
  view for orphaned data page
  """

  template_name = 'bemas/orphaned-data.html'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add default elements to context
    context = add_default_context_elements(context, self.request.user)
    # add orphaned data to context
    orphaned_organizations = get_orphaned_organizations(Originator, Complaint, Organization)
    if orphaned_organizations:
      orphaned_organizations_list = []
      for orphaned_organization in orphaned_organizations:
        orphaned_organization_dict = {
          'link': reverse('bemas:organization_update', args=[orphaned_organization.pk]),
          'text': str(orphaned_organization)
        }
        orphaned_organizations_list.append(orphaned_organization_dict)
      context['orphaned_organizations'] = orphaned_organizations_list
    orphaned_persons = get_orphaned_persons(Complaint, Contact, Person)
    if orphaned_persons:
      orphaned_persons_list = []
      for orphaned_person in orphaned_persons:
        orphaned_person_dict = {
          'link': reverse('bemas:person_update', args=[orphaned_person.pk]),
          'text': str(orphaned_person)
        }
        orphaned_persons_list.append(orphaned_person_dict)
      context['orphaned_persons'] = orphaned_persons_list
    orphaned_originators = get_orphaned_originators(Complaint, Originator)
    if orphaned_originators:
      orphaned_originators_list = []
      for orphaned_originator in orphaned_originators:
        orphaned_originator_dict = {
          'link': reverse('bemas:originator_update', args=[orphaned_originator.pk]),
          'text': str(orphaned_originator)
        }
        orphaned_originators_list.append(orphaned_originator_dict)
      context['orphaned_originators'] = orphaned_originators_list
    # add complaint status change deadline date to context
    context['deadline_date'] = get_complaint_status_change_deadline_date(True)
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
