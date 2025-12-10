import json

from django.conf import settings
from django.forms import ModelForm, ModelMultipleChoiceField, widgets
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView


class TagMultipleChoiceField(ModelMultipleChoiceField):
  def _check_values(self, value):
    from ..models.base import Tag

    key = self.to_field_name or 'pk'
    value = list(set(value))
    pks = []
    names = []

    for item in value:
      if str(item).isdigit():
        pks.append(str(item))
      else:
        names.append(item)

    qs = self.queryset.filter(**{'%s__in' % key: pks})
    found_tags_map = {str(getattr(t, key)): t for t in qs}
    found_tags = list(found_tags_map.values())

    for pk in pks:
      if pk not in found_tags_map:
        names.append(pk)

    for name in names:
      if str(name).strip():
        tag, created = Tag.objects.get_or_create(name=name)
        if tag not in found_tags:
          found_tags.append(tag)

    return found_tags

  def to_python(self, value):
    if not value:
      return []
    return list(self._check_values(value))


class DynamicStyledModelForm(ModelForm):
  """
  Eine ModelForm, die automatisch CSS-Klassen zu allen Feldern hinzufügt
  basierend auf ihrem Widget-Typ.
  """

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    # Mapping: Widget-Typ → CSS-Klassen und zusätzliche HTML-Attribute
    widget_config = {
      widgets.TextInput: {
        'class': 'form-control text-input',
        'autocomplete': 'off',
        'spellcheck': 'false',
      },
      widgets.NumberInput: {
        'class': 'form-control number-input',
        'step': 'any',
        'autocomplete': 'off',
      },
      widgets.EmailInput: {
        'class': 'form-control email-input',
        'autocomplete': 'email',
        'spellcheck': 'false',
      },
      widgets.URLInput: {
        'class': 'form-control url-input',
        'autocomplete': 'url',
        'spellcheck': 'false',
      },
      widgets.PasswordInput: {
        'class': 'form-control password-input',
        'autocomplete': 'current-password',
      },
      widgets.Select: {'class': 'form-control form-select select-input'},
      widgets.SelectMultiple: {'class': 'form-select select2-multiple'},
      widgets.Textarea: {
        'class': 'form-control textarea-input',
        'rows': '4',
        'spellcheck': 'true',
      },
      widgets.CheckboxInput: {'class': 'form-check-input checkbox-input'},
      widgets.DateInput: {'class': 'form-control date-input', 'autocomplete': 'off'},
      widgets.TimeInput: {'class': 'form-control time-input', 'autocomplete': 'off'},
      widgets.DateTimeInput: {'class': 'form-control datetime-input', 'autocomplete': 'off'},
      widgets.FileInput: {'class': 'form-control'},
      widgets.ClearableFileInput: {'class': 'form-control'},
    }

    # Durch alle Felder iterieren
    for field_name, field in self.fields.items():
      widget_type = type(field.widget)

      # Passende Konfiguration für diesen Widget-Typ finden
      if widget_type in widget_config:
        config = widget_config[widget_type]

        # CSS-Klassen behandeln (bestehende erhalten)
        if 'class' in config:
          existing_classes = field.widget.attrs.get('class', '')
          new_classes = config['class']

          if existing_classes:
            field.widget.attrs['class'] = f'{existing_classes} {new_classes}'
          else:
            field.widget.attrs['class'] = new_classes

        # Alle anderen Attribute aus der Konfiguration hinzufügen
        for attr_name, attr_value in config.items():
          if attr_name != 'class':  # CSS-Klassen wurden bereits behandelt
            field.widget.attrs[attr_name] = attr_value

      # Zusätzliche Attribute für bessere UX (nur wenn kein Placeholder bereits gesetzt)
      if (
        not isinstance(field.widget, widgets.CheckboxInput)
        and 'placeholder' not in field.widget.attrs
      ):
        field.widget.attrs.update(
          {'placeholder': field.label or field_name.replace('_', ' ').title()}
        )

      # HTML5-Validierung unterstützen
      if field.required:
        field.widget.attrs['required'] = 'required'


class GenericCreateView(CreateView):
  template_name = 'kiju/form.html'
  model = None
  success_url = None

  def __init__(self, model, *args, **kwargs):
    self.model = model
    self.success_url = reverse_lazy(viewname=f'kiju:{self.model.__name__.lower()}_list')

  def dispatch(self, request, *args, **kwargs):
    self.fields = '__all__'
    return super().dispatch(request, *args, **kwargs)

  def get_form_class(self):
    used_model = self.model

    class StyledForm(DynamicStyledModelForm):
      class Meta:
        model = used_model
        fields = '__all__'

      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Wenn das Modell ein Geometrie-Feld hat, verwende LeafletWidget
        if 'geometry' in self.fields:
          from leaflet.forms.widgets import LeafletWidget

          self.fields['geometry'].widget = LeafletWidget()

        if 'tags' in self.fields:
          from ..models.base import Tag

          current_field = self.fields['tags']
          self.fields['tags'] = TagMultipleChoiceField(
            queryset=Tag.objects.all(),
            label=current_field.label,
            required=current_field.required,
            widget=widgets.SelectMultiple(
              attrs={'class': 'form-select select2-multiple', 'data-tags': 'true'}
            ),
          )

    return StyledForm

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)

    # Model-Informationen hinzufügen
    context['model_verbose_name'] = self.model._meta.verbose_name
    context['model_verbose_name_plural'] = self.model._meta.verbose_name_plural
    context['model_name'] = self.model.__name__
    context['model_lower'] = self.model.__name__.lower()
    context['model_icon'] = getattr(self.model, 'icon', None)

    context['LEAFLET_CONFIG'] = getattr(
      settings,
      'LEAFLET_CONFIG',
      {
        'DEFAULT_CENTER': (51.0, 10.0),
        'DEFAULT_ZOOM': 6,
        'MIN_ZOOM': 3,
        'MAX_ZOOM': 18,
      },
    )

    return context


class GenericUpdateView(UpdateView):
  template_name = 'kiju/form.html'
  model = None
  success_url = None

  def __init__(self, model, *args, **kwargs):
    self.model = model
    self.success_url = reverse_lazy(viewname=f'kiju:{self.model.__name__.lower()}_list')

  def dispatch(self, request, *args, **kwargs):
    self.fields = '__all__'
    return super().dispatch(request, *args, **kwargs)

  def get_form_class(self):
    used_model = self.model

    class StyledForm(DynamicStyledModelForm):
      class Meta:
        model = used_model
        fields = '__all__'

      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Wenn das Modell ein Geometrie-Feld hat, verwende LeafletWidget
        if 'geometry' in self.fields:
          from leaflet.forms.widgets import LeafletWidget

          self.fields['geometry'].widget = LeafletWidget()

        if 'tags' in self.fields:
          from ..models.base import Tag

          current_field = self.fields['tags']
          self.fields['tags'] = TagMultipleChoiceField(
            queryset=Tag.objects.all(),
            label=current_field.label,
            required=current_field.required,
            widget=widgets.SelectMultiple(
              attrs={'class': 'form-select select2-multiple', 'data-tags': 'true'}
            ),
          )

    return StyledForm

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)

    # Model-Informationen hinzufügen
    context['model_verbose_name'] = self.model._meta.verbose_name
    context['model_verbose_name_plural'] = self.model._meta.verbose_name_plural
    context['model_name'] = self.model.__name__
    context['model_lower'] = self.model.__name__.lower()
    context['model_icon'] = getattr(self.model, 'icon', None)
    context['is_update'] = True  # Kennzeichnung für Update-Operation

    context['LEAFLET_CONFIG'] = getattr(
      settings,
      'LEAFLET_CONFIG',
      {
        'DEFAULT_CENTER': (51.0, 10.0),
        'DEFAULT_ZOOM': 6,
        'MIN_ZOOM': 3,
        'MAX_ZOOM': 18,
      },
    )

    # Geometrie zu GeoJSON konvertieren, falls vorhanden
    print(self.object.__dict__)
    if hasattr(self.object, 'geometry') and self.object.geometry:
      try:
        geom = self.object.geometry
        # Transformiere von EPSG:25833 zu EPSG:4326
        geom_transformed = geom.transform(4326, clone=True)
        # Konvertiere zu GeoJSON
        geojson = json.loads(geom_transformed.geojson)
        context['geometry'] = json.dumps(geojson)
        context['model_geometry_type'] = geom.geom_type
        print(f'Geometrietyp: {geom.geom_type}')
      except Exception as e:
        print(f'Error converting geometry: {e}')
        context['geometry'] = None
    else:
      context['geometry'] = None

    return context


class GenericDeleteView(DeleteView):
  template_name = 'kiju/delete.html'
  model = None
  success_url = None

  def __init__(self, model, *args, **kwargs):
    self.model = model
    self.success_url = reverse_lazy(viewname=f'kiju:{self.model.__name__.lower()}_list')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)

    # Model-Informationen hinzufügen
    context['model_verbose_name'] = self.model._meta.verbose_name
    context['model_verbose_name_plural'] = self.model._meta.verbose_name_plural
    context['model_name'] = self.model.__name__
    context['model_lower'] = self.model.__name__.lower()

    return context

  def delete(self, request, *args, **kwargs):
    """
    Überschreibt die delete-Methode, um AJAX-Anfragen zu unterstützen.
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
      try:
        # Objekt löschen
        self.object = self.get_object()
        self.object.delete()

        # Erfolgsmeldung zurückgeben
        return JsonResponse(
          {
            'success': True,
            'message': f'{self.model._meta.verbose_name} wurde erfolgreich gelöscht.',
          }
        )
      except Exception as e:
        # Fehlermeldung zurückgeben
        return JsonResponse(
          {'success': False, 'message': f'Fehler beim Löschen: {str(e)}'}, status=400
        )
    else:
      # Normale Behandlung für nicht-AJAX-Anfragen
      return super().delete(request, *args, **kwargs)
