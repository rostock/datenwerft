from django.contrib.gis.geos import GEOSGeometry
from django.contrib.messages import success
from django.forms.models import modelform_factory
from django.urls import reverse
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from ..models import Fmf, PaketUmwelt
from .forms import ObjectForm
from .functions import (
  add_model_context_elements,
  add_permissions_context_elements,
  add_useragent_context_elements,
  assign_widget,
  geometry_keeper,
  get_referer,
  get_referer_url,
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


class TableView(TemplateView):
  """
  view for table page

  :param template_name: template name
  """

  template_name = 'fmm/dummy.html'

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
    # add to context: URLs
    context['cancel_url'] = reverse('fmm:index')
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
  template_name = None
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
    self.object = form.save()
    success(
      self.request, self.success_message.format(self.model._meta.verbose_name, str(self.object))
    )
    return super().form_valid(form)

  def form_invalid(self, form, **kwargs):
    """
    re-opens passed form if it is not valid
    (purpose: keep original referer and geometry, if necessary)

    :param form: form
    :return: passed form if it is not valid
    """
    context_data = self.get_context_data(form=form)
    form.data = form.data.copy()
    context_data = geometry_keeper(form.data, context_data)
    context_data['form'] = form
    context_data['cancel_url'] = form.data.get('original_referer', None)
    return self.render_to_response(context_data)

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
    # add disabled fields to context, if necessary
    else:
      context['disabled_fields'] = ['fmf']
    # add to context: URLs
    if self.cancel_url:
      context['cancel_url'] = reverse(self.cancel_url)
    else:
      context['cancel_url'] = reverse('fmm:index')
    return context

  def get_success_url(self):
    """
    defines the URL called in case of successful request

    :return: URL called in case of successful request
    """
    referer = self.request.POST.get('original_referer', '')
    if 'table' in referer:
      return reverse('fmm:table')
    elif 'map' in referer:
      return reverse('fmm:map')
    elif 'show' in referer:
      return reverse('fmm:show')
    return reverse('fmm:index')


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


class ObjectDeleteView(DeleteView):
  """
  generic view for form page for deleting an instance of an object

  :param model: model
  :param template_name: template name
  :param success_message: custom success message
  """

  model = None
  template_name = 'fmm/delete.html'
  success_message = '{} <strong><em>{}</em></strong> erfolgreich gelöscht!'

  def form_valid(self, form):
    """
    sends HTTP response if passed form is valid

    :param form: form
    :return: HTTP response if passed form is valid
    """
    success(
      self.request, self.success_message.format(self.model._meta.verbose_name, str(self.object))
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
    # add to context: URLs
    context['cancel_url'] = get_referer_url(
      referer=get_referer(self.request), fallback='fmm:index'
    )
    return context

  def get_success_url(self):
    """
    defines the URL called in case of successful request

    :return: URL called in case of successful request
    """
    referer = self.request.POST.get('original_referer', '')
    if 'table' in referer:
      return reverse('fmm:table')
    elif 'map' in referer:
      return reverse('fmm:map')
    elif 'show' in referer:
      return reverse('fmm:show')
    return reverse('fmm:index')


class FmfCreateView(ObjectCreateView):
  """
  view for form page for creating a FMF instance

  :param model: model
  :param template_name: template name
  """

  model = Fmf
  template_name = 'fmm/form_fmf.html'


class FmfUpdateView(ObjectUpdateView):
  """
  view for form page for updating a FMF instance

  :param model: model
  :param template_name: template name
  """

  model = Fmf
  template_name = 'fmm/form_fmf.html'


class FmfDeleteView(ObjectDeleteView):
  """
  view for form page for deleting a FMF instance

  :param model: model
  """

  model = Fmf


class PaketUmweltCreateView(ObjectCreateView):
  """
  view for form page for creating a Paket Umwelt instance

  :param model: model
  :param template_name: template name
  """

  model = PaketUmwelt
  template_name = 'fmm/form_paket.html'


class PaketUmweltUpdateView(ObjectUpdateView):
  """
  view for form page for updating a Paket Umwelt instance

  :param model: model
  :param template_name: template name
  """

  model = PaketUmwelt
  template_name = 'fmm/form_paket.html'


class PaketUmweltDeleteView(ObjectDeleteView):
  """
  view for form page for deleting a Paket Umwelt instance

  :param model: model
  """

  model = PaketUmwelt
