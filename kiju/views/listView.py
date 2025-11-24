from django.views.generic import TemplateView
from django_datatables_view.base_datatable_view import BaseDatatableView


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

  def __init__(self, *args, **kwargs):
    self.model = kwargs.pop('model', None)
    super().__init__(*args, **kwargs)
    if self.model:
      self.model_name = self.model.__name__
      self.model_lower = self.model_name.lower()
      self.model_verbose_name = getattr(self.model._meta, 'verbose_name', self.model_name)
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
    if self.model:
      queryset = self.model.objects.all()
      context['model'] = self.model
      context['model_name'] = self.model_name or self.model.__name__
      context['model_lower'] = self.model_lower or self.model.__name__.lower()
      context['model_verbose_name'] = self.model_verbose_name or getattr(
        self.model._meta,
        'verbose_name',
        self.model.__name__,
      )
      context['model_dict'] = self.model_dict or {}
      context['object_list'] = queryset
      context['objects'] = queryset
      if hasattr(self.model, 'list_fields'):
        context['list_fields'] = self.model.list_fields
    return context
