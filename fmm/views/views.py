from django.contrib.gis.geos import GEOSGeometry
from django.contrib.messages import success
from django.forms.models import modelform_factory
from django.urls import reverse
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView

from ..models import Fmf
from .forms import ObjectForm
from .functions import (
  add_model_context_elements,
  add_permissions_context_elements,
  add_useragent_context_elements,
  assign_widget,
  geometry_keeper,
)


class IndexView(TemplateView):
  """
  view for main page

  :param template_name: template name
  """

  template_name = 'fmm/index.html'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add user agent related context elements
    context = add_useragent_context_elements(context, self.request)
    # add permissions related context elements
    context = add_permissions_context_elements(context, self.request.user)
    return context


class ObjectMixin:
  """
  generic mixin for form page for creating or updating an instance of an object

  :param model: model
  :param template_name: template name
  :param form: form
  :param success_message: custom success message
  :param cancel_url: custom cancel URL
  """

  model = None
  template_name = 'fmm/form_fmf.html'
  form = ObjectForm
  success_message = ''
  cancel_url = None

  def get_form_class(self):
    # ensure the model is set before creating the form class
    if not self.model:
      raise ValueError('The model attribute must be set before calling get_form_class.')
    # dynamically create the form class
    form_class = modelform_factory(
      self.model, form=self.form, fields='__all__', formfield_callback=assign_widget
    )
    return form_class

  def form_valid(self, form):
    """
    sends HTTP response if passed form is valid

    :param form: form
    :return: HTTP response if passed form is valid
    """
    success(
      self.request, self.success_message.format(self.model._meta.verbose_name, str(form.instance))
    )
    return super().form_valid(form)

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add user agent related context elements
    context = add_useragent_context_elements(context, self.request)
    # add permissions related context elements
    context = add_permissions_context_elements(context, self.request.user)
    # add model related context elements
    context = add_model_context_elements(context, self.model)
    # add geometry to context, if necessary
    if issubclass(self.model, Fmf):
      if self.object:
        # GeoJSONify geometry
        geometry = getattr(self.object, self.model.BaseMeta.geometry_field)
        if geometry:
          context['geometry'] = GEOSGeometry(geometry).geojson
    # add to context: URLs
    if self.cancel_url:
      context['cancel_url'] = reverse(self.cancel_url)
    else:
      context['cancel_url'] = reverse('fmm:index')
    return context


class ObjectCreateView(ObjectMixin, CreateView):
  """
  generic view for form page for creating an instance of an object

  :param success_message: custom success message
  """

  success_message = '{} <strong><em>{}</em></strong> erfolgreich gespeichert!'


class ObjectUpdateView(ObjectMixin, UpdateView):
  """
  generic view for form page for updating an instance of an object

  :param success_message: custom success message
  """

  success_message = '{} <strong><em>{}</em></strong> erfolgreich aktualisiert!'


class FmfCreateView(ObjectCreateView):
  """
  view for form page for creating a FMF instance

  :param model: model
  """

  model = Fmf

  def form_invalid(self, form, **kwargs):
    """
    re-opens passed form if it is not valid
    (purpose: keep geometry)

    :param form: form
    :return: passed form if it is not valid
    """
    context_data = self.get_context_data(form=form)
    form.data = form.data.copy()
    context_data = geometry_keeper(form.data, context_data)
    context_data['form'] = form
    return self.render_to_response(context_data)


class FmfUpdateView(ObjectUpdateView):
  """
  view for form page for updating a FMF instance

  :param model: model
  """

  model = Fmf
