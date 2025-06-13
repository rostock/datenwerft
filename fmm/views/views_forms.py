from django.contrib.gis.forms.fields import PolygonField
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.messages import success
from django.forms import ModelForm, ValidationError
from django.forms.models import modelform_factory
from django.urls import reverse
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from ..models import Fmf, PaketUmwelt
from .functions import (
  add_model_context_elements,
  add_permissions_context_elements,
  add_useragent_context_elements,
  assign_widget,
  geometry_keeper,
  get_referer,
  get_referer_url,
)


class ObjectForm(ModelForm):
  """
  form for instances of an object

  :param required_css_class: CSS class for required field
  """

  required_css_class = 'required'

  def __init__(self, *args, **kwargs):
    kwargs.setdefault('label_suffix', '')
    super().__init__(*args, **kwargs)
    # customize messages
    for field in self.fields.values():
      required_message = 'Das Attribut <strong><em>{}</em></strong> ist Pflicht!'.format(
        field.label
      )
      unique_message = '{} mit angegebenem Wert im Attribut <strong><em>{}</em></strong>'.format(
        self._meta.model._meta.verbose_name, field.label
      )
      unique_message += ' existiert bereits!'
      field.error_messages = {'required': required_message, 'unique': unique_message}
      if issubclass(field.__class__, PolygonField):
        required_message = '<strong><em>{}</em></strong> muss in Karte gezeichnet werden!'.format(
          field.label
        )
        field.error_messages = {
          'required': '',
          'invalid_geom': required_message,
          'invalid_geom_type': required_message,
        }

  def clean(self):
    """
    cleans fields
    """
    cleaned_data = super().clean()
    # clean geometry field, if necessary
    if self._meta.model.BaseMeta.geometry_field is not None:
      geometry_field_name = self._meta.model.BaseMeta.geometry_field
      geometry = cleaned_data.get(geometry_field_name)
      if 'EMPTY' in str(geometry):
        geometry_field = self.fields[geometry_field_name]
        raise ValidationError(
          '<strong><em>{}</em></strong> muss in Karte gezeichnet werden!'.format(
            geometry_field.label
          )
        )
      cleaned_data[geometry_field_name] = geometry
    return cleaned_data


class ObjectMixin:
  """
  generic mixin for form page for creating or updating an instance of an object

  :param model: model
  :param template_name: template name
  :param form: form
  :param success_message: custom success message
  :param referer_url: custom referer URL
  """

  model = None
  template_name = None
  form = ObjectForm
  success_message = ''
  referer_url = 'fmm:index'

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
    (purpose: keep original referer URL and geometry, if necessary)

    :param form: form
    :return: passed form if it is not valid
    """
    context_data = self.get_context_data(form=form)
    form.data = form.data.copy()
    context_data = geometry_keeper(form.data, context_data)
    context_data['form'] = form
    context_data['referer_url'] = form.data.get('original_referer_url', None)
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
    # add custom referer URL to context
    context['referer_url'] = get_referer_url(
      referer=get_referer(self.request), fallback=self.referer_url
    )
    return context

  def get_success_url(self):
    """
    defines the URL called in case of successful request

    :return: URL called in case of successful request
    """
    referer_url = self.request.POST.get('original_referer_url', '')
    return referer_url if referer_url else reverse(self.referer_url)


class ObjectCreateView(ObjectMixin, CreateView):
  """
  generic view for form page for creating an instance of an object

  :param success_message: custom success message
  """

  success_message = '{} <strong><em>{}</em></strong> erfolgreich gespeichert!'


class PaketCreateView(ObjectCreateView):
  """
  generic view for form page for creating a "Paket" instance
  """

  def form_invalid(self, form, **kwargs):
    """
    re-opens passed form if it is not valid
    (purpose: keep original initial field values)

    :param form: form
    :return: passed form if it is not valid
    """
    initial_fmf = self.get_initial().get('fmf')
    if not form.data.get('fmf') and initial_fmf:
      data = form.data.copy()
      data['fmf'] = str(initial_fmf.pk)
      form.data = data
    return self.render_to_response(self.get_context_data(form=form))

  def get_initial(self):
    """
    conditionally sets initial field values

    :return: dictionary with initial field values
    """
    # get corresponding FMF object via primary key passed as URL parameter
    # and set corresponding initial field value
    if self.kwargs.get('fmf_pk', None):
      return {'fmf': Fmf.objects.get(pk=self.kwargs.get('fmf_pk'))}
    return {}


class ObjectUpdateView(ObjectMixin, UpdateView):
  """
  generic view for form page for updating an instance of an object

  :param success_message: custom success message
  """

  success_message = '{} <strong><em>{}</em></strong> erfolgreich bearbeitet!'


class ObjectDeleteView(DeleteView):
  """
  generic view for form page for deleting an instance of an object

  :param model: model
  :param template_name: template name
  :param success_message: custom success message
  :param referer_url: custom referer URL
  """

  model = None
  template_name = 'fmm/delete.html'
  success_message = '{} <strong><em>{}</em></strong> erfolgreich gelöscht!'
  referer_url = 'fmm:index'

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
    # add custom referer URL to context
    context['referer_url'] = get_referer_url(
      referer=get_referer(self.request), fallback=self.referer_url
    )
    return context

  def get_success_url(self):
    """
    defines the URL called in case of successful request

    :return: URL called in case of successful request
    """
    referer_url = self.request.POST.get('original_referer_url', '')
    return referer_url if referer_url else reverse(self.referer_url)


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


class PaketUmweltCreateView(PaketCreateView):
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
