from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import resolve_url
from django.urls import reverse
from django_datatables_view.base_datatable_view import BaseDatatableView

from bemas.utils import generate_user_string
from d3.models import Vorgang
from d3.utils import fetch_processes, lade_akten_ordner, lade_d3_session_id
from datenwerft.settings import D3_ENABLED, D3_HOST, D3_REPOSITORY


class TableProcessView(BaseDatatableView):
  object_id: str = ''

  """
  view to return JSON data for Vorgang model
  """

  def __init__(self, model=None, *args, **kwargs):
    self.model = Vorgang
    model_name = self.model.__name__
    model_name_lower = model_name.lower()
    self.model_name = model_name
    self.model_name_lower = model_name_lower
    if model is not None:
      self.datenmanagement_model_name = model.__name__
      self.datenmanagement_model_lower = self.datenmanagement_model_name.lower()
      self.content_type_id = ContentType.objects.get(
        app_label='datenmanagement', model=self.datenmanagement_model_lower
      ).id
    else:
      self.datenmanagement_model_name = ''
      self.datenmanagement_model_lower = ''
      self.content_type_id = None

    self.columns = list(self.model.BasemodelMeta.list_fields.keys()) + ['control']

    super().__init__(*args, **kwargs)

  def get_initial_queryset(self):
    self.object_id = self.kwargs.get('pk')
    qs = fetch_processes(self.content_type_id, self.kwargs.get('pk'))
    if qs is None:
      return Vorgang.objects.none()  # Avoid NoneType crash
    return qs

  def prepare_results(self, qs):
    results = []

    for obj in qs:
      row = []

      for field in self.columns:
        if field == 'control':
          continue
        value = getattr(obj, field)
        if hasattr(value, 'strftime'):
          value = value.strftime('%d.%m.%Y, %H:%M:%S Uhr')
        elif field == 'akten':
          url = f'{D3_HOST}/dms/r/{D3_REPOSITORY}/o2/{value.d3_id}'
          title = 'Akte in d.3 öffnen…'
          value = f'<a title="{title}" target="_blank" href="{url}">{value.d3_id}</a>'
        elif field == 'd3_id':
          url = f'{D3_HOST}/dms/r/{D3_REPOSITORY}/o2/{value}'
          title = 'Vorgang in d.3 öffnen…'
          value = f'<a title="{title}" target="_blank" href="{url}">{value}</a>'
        elif field == 'erstellt_durch':
          user = User.objects.get(username=value)
          value = generate_user_string(user)
        elif value is None:
          value = ''
        else:
          value = str(value)
        row.append(value)

      upload_url = resolve_url(
        'd3:' + self.datenmanagement_model_name + '_d3_add_file', self.object_id, obj.id
      )
      upload_link = f'<a href="{upload_url}" title="Dokument anlegen…">'
      upload_link += '<i class="fa fa-file-import"></i></a>'
      expand_element = '<i class="fa fa-circle-info" style="cursor:pointer"</i>'
      row.append(upload_link + expand_element)
      results.append(row)

    return results


class D3ContextMixin:
  def get_d3_context(self, context, model, pk):
    context['enabled'] = False
    if D3_ENABLED:
      model_name = model.__name__
      content_type_id = ContentType.objects.get(
        app_label='datenmanagement', model=model_name.lower()
      ).id
      akten_ordner = lade_akten_ordner(content_type_id)
      if akten_ordner is not None:
        context['enabled'] = True
        if lade_d3_session_id(self.request) is None:
          context['authentication_failed'] = True
        else:
          context['column_titles'] = list(Vorgang.BasemodelMeta.list_fields.values())
          context['url_process_tabledata'] = reverse(
            'd3:' + model_name + '_fetch_process_list', kwargs={'pk': pk}
          )
          context['url_process_metadata'] = reverse(
            'd3:' + model_name + '_fetch_metadata',
          )
          context['url_process_add'] = reverse(
            'd3:' + model_name + '_d3_add_process', kwargs={'pk': pk}
          )

    return context
