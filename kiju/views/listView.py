from django.views.generic import TemplateView
from django_datatables_view.base_datatable_view import BaseDatatableView

from ..utils import get_user_provider, is_angebotsdb_admin
from .functions import add_permission_context_elements


class DataTableView(BaseDatatableView):
  model = None


class ListView(TemplateView):
  """
  View for the Table page of KiJu.
  """

  template_name = 'kiju/list.html'
  model = None
  model_name = None
  model_lower = None
  model_verbose_name = None
  model_dict = None

  def dispatch(self, request, *args, **kwargs):
    """
    Check if user has permission to access the view.
    """
    return super().dispatch(request, *args, **kwargs)

  def __init__(self, *args, **kwargs):
    self.model = kwargs.pop('model', None)
    super().__init__(*args, **kwargs)
    if self.model:
      self.model_name = self.model.__name__
      self.model_lower = self.model_name.lower()
      self.model_verbose_name = getattr(self.model._meta, 'verbose_name', self.model_name)
      self.model_verbose_name_plural = getattr(
        self.model._meta, 'verbose_name_plural', self.model_name
      )
      self.model_dict = {
        field.name: {
          'verbose_name': getattr(field, 'verbose_name', field.name),
          'type': field.get_internal_type(),
        }
        for field in self.model._meta.get_fields()
        if getattr(field, 'concrete', False) and not getattr(field, 'many_to_many', False)
      }

  def get_context_data(self, **kwargs):
    """
    returns a dictionary containing the context data for the index page.
    """
    context = super().get_context_data(**kwargs)
    context = add_permission_context_elements(context, self.request.user)
    if self.model:
      from ..models.services import Service

      is_service_model = not self.model._meta.abstract and issubclass(self.model, Service)

      if is_service_model:
        if self.request.user.is_superuser or is_angebotsdb_admin(self.request.user):
          # Admins sehen nur die Originale — Draft-Copies sind über die
          # Review-Inbox zugänglich, nicht über die normale Listenansicht.
          queryset = self.model.objects.filter(published_version__isnull=True)
        else:
          provider = get_user_provider(self.request.user)
          if provider:
            # Provider sehen:
            # 1. Alle eigenen originalen Services (published_version=None)
            # 2. Eigene Draft-Copies als separate Einträge mit eigenem Status-Badge
            queryset = self.model.objects.filter(host=provider)
          else:
            # Nutzer ohne OE sehen alle originalen Services (wie Admins),
            # aber ohne Zugriff auf Draft-Copies
            queryset = self.model.objects.filter(published_version__isnull=True)
      else:
        queryset = self.model.objects.all()

      # Hierarchische Liste für das Template aufbauen:
      # Bei Providern erscheinen Forks (Draft-Copies) direkt unter ihrem Original
      # mit Sub-Nummerierung (1.1, 2.1, ...) und Einrückung.
      provider = get_user_provider(self.request.user) if is_service_model else None
      provider_with_forks = (
        is_service_model
        and not (self.request.user.is_superuser or is_angebotsdb_admin(self.request.user))
        and provider
      )
      if provider_with_forks:
        originals = queryset.filter(published_version__isnull=True)
        annotated_objects = []
        parent_num = 0
        for svc in originals:
          parent_num += 1
          copies = list(queryset.filter(published_version=svc))
          has_draft = len(copies) > 0
          annotated_objects.append(
            {
              'obj': svc,
              'display_number': str(parent_num),
              'is_fork': False,
              'tree_prefix': '',
              'has_draft_copy': has_draft,
            }
          )
          for j, copy in enumerate(copies):
            tree_char = '└─' if j == len(copies) - 1 else '├─'
            annotated_objects.append(
              {
                'obj': copy,
                'display_number': f'{parent_num}.{j + 1}',
                'is_fork': True,
                'tree_prefix': tree_char,
                'has_draft_copy': False,
              }
            )
      else:
        annotated_objects = [
          {
            'obj': obj,
            'display_number': str(i),
            'is_fork': False,
            'tree_prefix': '',
            'has_draft_copy': False,
          }
          for i, obj in enumerate(queryset, start=1)
        ]

      context['model'] = self.model
      context['model_name'] = self.model_name or self.model.__name__
      context['model_lower'] = self.model_lower or self.model.__name__.lower()
      context['model_verbose_name'] = self.model_verbose_name or getattr(
        self.model._meta,
        'verbose_name',
        self.model.__name__,
      )
      context['model_verbose_name_plural'] = self.model_verbose_name_plural or getattr(
        self.model._meta,
        'verbose_name_plural',
        self.model.__name__,
      )
      context['model_dict'] = self.model_dict or {}
      context['object_list'] = queryset
      context['objects'] = queryset
      context['annotated_objects'] = annotated_objects

      if hasattr(self.model, 'list_fields'):
        context['list_fields'] = self.model.list_fields
      context['model_icon'] = getattr(self.model, 'icon', None)
      context['model_icon_plural'] = getattr(self.model, 'icon_plural', None)

      # Provider-Informationen für Service-Modelle
      context['is_service_model'] = is_service_model

      if is_service_model:
        if self.request.user.is_superuser or is_angebotsdb_admin(self.request.user):
          context['user_provider'] = '__all__'
        else:
          context['user_provider'] = get_user_provider(self.request.user)
      else:
        context['user_provider'] = '__all__'

    return context
