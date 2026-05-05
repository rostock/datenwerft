from django.views.generic.base import TemplateView

from stadtbereichskatalog.models import Category, Source

from .base import (
  TableDataView,
  TableView,
)
from .functions import (
  add_app_context_elements,
  add_permissions_context_elements,
  add_useragent_context_elements,
)


class IndexView(TemplateView):
  """
  view for main page

  :param template_name: template name
  """

  template_name = 'stadtbereichskatalog/index.html'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add user agent related context elements
    context = add_useragent_context_elements(context, self.request)
    # add global app related context elements
    context = add_app_context_elements(context)
    # add permissions related context elements
    context = add_permissions_context_elements(context, self.request.user)
    return context


class CategoryTableDataView(TableDataView):
  """
  view for composing table data out of instances of object:
  Themenbereich und/oder Kategorie

  :param model: model
  :param edit_view_name: name of view for form page for editing
  """

  model = Category
  edit_view_name = 'stadtbereichskatalog:category_edit'


class CategoryTableView(TableView):
  """
  view for table page for instances of general object:
  Themenbereich und/oder Kategorie

  :param model: model
  :param table_data_view_name: name of view for composing table data out of instances
  :param icon_name: icon name
  """

  model = Category
  table_data_view_name = 'stadtbereichskatalog:category_tabledata'
  icon_name = 'category'


class SourceTableDataView(TableDataView):
  """
  view for composing table data out of instances of object:
  Quellenangabe

  :param model: model
  :param edit_view_name: name of view for form page for editing
  """

  model = Source
  edit_view_name = 'stadtbereichskatalog:source_edit'


class SourceTableView(TableView):
  """
  view for table page for instances of general object:
  Quellenangabe

  :param model: model
  :param table_data_view_name: name of view for composing table data out of instances
  :param icon_name: icon name
  """

  model = Source
  table_data_view_name = 'stadtbereichskatalog:source_tabledata'
  icon_name = 'source'
