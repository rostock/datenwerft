from django.views.generic.base import TemplateView

from stadtbereichskatalog.models import Category, Indicator, Source, Topic

from ..apps import StadtbereichskatalogConfig as appConfig
from .base import (
  MetadataEditView,
  MetadataTableDataView,
  MetadataTableView,
)
from .functions import (
  add_app_context_elements,
  add_permissions_context_elements,
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
    # add global app related context elements
    context = add_app_context_elements(context)
    # add permissions related context elements
    context = add_permissions_context_elements(context, self.request.user)
    return context


class TopicTableDataView(MetadataTableDataView):
  """
  view for composing table data out of instances of metadata model class:
  Themenbereich

  :param model: model
  :param edit_view_name: name of view for form page for editing
  """

  model = Topic
  edit_view_name = f'{appConfig.name}:topic_edit'


class TopicTableView(MetadataTableView):
  """
  view for table page for instances of metadata model class:
  Themenbereich

  :param model: model
  :param table_data_view_name: name of view for composing table data
  :param icon_name: icon name
  """

  model = Topic
  table_data_view_name = f'{appConfig.name}:topic_tabledata'
  icon_name = 'topic'


class TopicEditView(MetadataEditView):
  """
  view for form page for editing an instance of metadata model class:
  Themenbereich

  :param model: model
  :param cancel_url: custom cancel URL
  """

  model = Topic
  cancel_url = f'{appConfig.name}:topic_table'


class CategoryTableDataView(MetadataTableDataView):
  """
  view for composing table data out of instances of metadata model class:
  Kategorie

  :param model: model
  :param edit_view_name: name of view for form page for editing
  """

  model = Category
  edit_view_name = f'{appConfig.name}:category_edit'


class CategoryTableView(MetadataTableView):
  """
  view for table page for instances of metadata model class:
  Kategorie

  :param model: model
  :param table_data_view_name: name of view for composing table data
  :param icon_name: icon name
  """

  model = Category
  table_data_view_name = f'{appConfig.name}:category_tabledata'
  icon_name = 'category'


class CategoryEditView(MetadataEditView):
  """
  view for form page for editing an instance of metadata model class:
  Kategorie

  :param model: model
  :param cancel_url: custom cancel URL
  """

  model = Category
  cancel_url = f'{appConfig.name}:category_table'


class SourceTableDataView(MetadataTableDataView):
  """
  view for composing table data out of instances of metadata model class:
  Quellenangabe

  :param model: model
  :param edit_view_name: name of view for form page for editing
  """

  model = Source
  edit_view_name = f'{appConfig.name}:source_edit'


class SourceTableView(MetadataTableView):
  """
  view for table page for instances of metadata model class:
  Quellenangabe

  :param model: model
  :param table_data_view_name: name of view for composing table data out of instances
  :param icon_name: icon name
  """

  model = Source
  table_data_view_name = f'{appConfig.name}:source_tabledata'
  icon_name = 'source'


class SourceEditView(MetadataEditView):
  """
  view for form page for editing an instance of metadata model class:
  Quellenangabe

  :param model: model
  :param cancel_url: custom cancel URL
  """

  model = Source
  cancel_url = f'{appConfig.name}:source_table'


class IndicatorTableDataView(MetadataTableDataView):
  """
  view for composing table data out of instances of metadata model class:
  Indikator

  :param model: model
  :param edit_view_name: name of view for form page for editing
  """

  model = Indicator
  edit_view_name = f'{appConfig.name}:indicator_edit'


class IndicatorTableView(MetadataTableView):
  """
  view for table page for instances of metadata model class:
  Indikator

  :param model: model
  :param table_data_view_name: name of view for composing table data out of instances
  :param icon_name: icon name
  """

  model = Indicator
  table_data_view_name = f'{appConfig.name}:indicator_tabledata'
  icon_name = 'indicator'


class IndicatorEditView(MetadataEditView):
  """
  view for form page for editing an instance of metadata model class:
  Indikator

  :param model: model
  :param cancel_url: custom cancel URL
  """

  model = Indicator
  cancel_url = f'{appConfig.name}:indicator_table'
