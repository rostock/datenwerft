from datenmanagement.models import Ansprechpartner_Baustellen
from django.apps import apps
from django.contrib.auth.models import Group, User
from django.contrib.messages import success
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.postgres.fields.array import ArrayField
from django.core.exceptions import PermissionDenied
from django.db import connections
from django.db.models import F
from django.forms import ChoiceField, ModelForm, TextInput, ValidationError
from django.forms.models import modelform_factory
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, UpdateView
from json import dumps
from operator import itemgetter
from re import sub
from time import time

from datenmanagement.utils import is_address_related_field, is_geometry_field
from .fields import AddressUUIDField, QuarterUUIDField, StreetUUIDField
from .functions import assign_widgets, get_thumb_url, set_form_attributes, \
  set_form_context_elements, set_model_related_context_elements


class DataForm(ModelForm):
  """
  definiert Basisformular

  :param *args
  :param **kwargs
  """

  required_css_class = 'required'

  def __init__(self, *args, **kwargs):
    associated_objects = kwargs.pop('associated_objects', None)
    associated_new = kwargs.pop('associated_new', None)
    fields_with_foreign_key_to_linkify = kwargs.pop(
        'fields_with_foreign_key_to_linkify', None)
    choices_models_for_choices_fields = kwargs.pop(
        'choices_models_for_choices_fields', None)
    group_with_users_for_choice_field = kwargs.pop(
        'group_with_users_for_choice_field', None)
    multi_foto_field = kwargs.pop('multi_foto_field', None)
    multi_files = kwargs.pop('multi_files', None)
    file = kwargs.pop('file', None)
    model = kwargs.pop('model', None)
    request = kwargs.pop('request', None)
    kwargs.setdefault('label_suffix', '')
    super(DataForm, self).__init__(*args, **kwargs)
    self.associated_objects = associated_objects
    self.associated_new = associated_new
    self.fields_with_foreign_key_to_linkify = fields_with_foreign_key_to_linkify
    self.choices_models_for_choices_fields = choices_models_for_choices_fields
    self.group_with_users_for_choice_field = group_with_users_for_choice_field
    self.multi_foto_field = multi_foto_field
    self.multi_files = multi_files
    self.file = file
    self.model = model
    self.request = request
    self.address_type = self.instance.BasemodelMeta.address_type
    self.address_mandatory = self.instance.BasemodelMeta.address_mandatory

    for field in self.model._meta.get_fields():
      # Textfelder gegebenenfalls in Auswahllisten umwandeln
      if field.name == 'ansprechpartner' or field.name == 'bearbeiter':
        if (
            self.group_with_users_for_choice_field
            and Group.objects.filter(name=self.group_with_users_for_choice_field).exists()
        ):
          users = list(
            User.objects.filter(
              groups__name=self.group_with_users_for_choice_field
            ).values('first_name', 'last_name', 'email')
          )
          # Sonderbehandlung für Datenmodell Baustellen (geplant):
          # hier zusätzliche Benutzer aus Codeliste holen
          if self.model.__name__ == 'Baustellen_geplant':
            additional_users = Ansprechpartner_Baustellen.objects.all()
            additional_users = additional_users.annotate(
              first_name=F('vorname'), last_name=F('nachname')
            ).values('first_name', 'last_name', 'email')
            additional_user_list = []
            for additional_user in list(additional_users):
              if additional_user['first_name'] is None:
                additional_user['first_name'] = 'zzz'
              if additional_user['last_name'] is None:
                additional_user['last_name'] = 'zzz'
              additional_user_list.append(additional_user)
            users += additional_user_list
          sorted_users = sorted(users, key=itemgetter('last_name', 'first_name', 'email'))
          user_list = []
          for user in sorted_users:
            if user['first_name'] != 'zzz' and user['last_name'] != 'zzz':
              user_list.append(
                user['first_name'] + ' ' + user['last_name'] + ' (' + user['email'].lower() + ')'
              )
            else:
              user_list.append(user['email'].lower())
          choices = [(user, user) for user in user_list]
          # Leerwert an erster Stelle einfügen
          choices.insert(0, ('', '---------'))
          choice_field = ChoiceField(
            label=field.verbose_name,
            choices=choices,
            initial=request.user.first_name +
            ' ' +
            request.user.last_name +
            ' (' +
            request.user.email.lower() +
            ')'
          )
          if field.name == 'ansprechpartner' or field.name == 'bearbeiter':
            self.fields[field.name] = choice_field
      # Adressfelder in eigenen Feldtyp umwandeln
      elif (field.name == 'adresse' or
            field.name == 'strasse' or
            field.name == 'gemeindeteil'):
        attrs = {
            'class': 'form-control',
            'autocapitalize': 'off',
            'autocomplete': 'off',
            'placeholder': ''
        }
        label = field.verbose_name
        required = self.address_mandatory
        if field.name == 'adresse':
          attrs['placeholder'] = 'Adresse eingeben…'
          self.fields[field.name] = AddressUUIDField(
              label=label,
              widget=TextInput(attrs=attrs),
              required=required
          )
        elif field.name == 'strasse':
          attrs['placeholder'] = 'Straße eingeben…'
          self.fields[field.name] = StreetUUIDField(
              label=label,
              widget=TextInput(attrs=attrs),
              required=required
          )
        else:
          attrs['placeholder'] = 'Gemeindeteil eingeben…'
          self.fields[field.name] = QuarterUUIDField(
              label=label,
              widget=TextInput(attrs=attrs),
              required=required
          )
      # bestimmte Modelle für bestimmte Felder zur Befüllung
      # entsprechender Auswahllisten heranziehen
      elif self.choices_models_for_choices_fields:
        choices_model_for_choices_field = self.choices_models_for_choices_fields.get(
            field.name)
        if choices_model_for_choices_field is not None:
          choices_model = apps.get_app_config(
              'datenmanagement').get_model(
              choices_model_for_choices_field)
          choices = []
          for choices_model_object in choices_model.objects.all():
            choices.append(
                (choices_model_object, choices_model_object))
          self.fields[field.name].choices = choices

    for field in self.fields.values():
      if field.label == 'Geometrie':
        required_message = 'Es muss ein Marker in der Karte gesetzt ' \
                           'werden bzw. eine Linie oder Fläche ' \
                           'gezeichnet werden, falls es sich um Daten ' \
                           'linien- oder flächenhafter Repräsentation ' \
                           'handelt!'
      else:
        required_message = 'Das Attribut <strong><em>{label}</em></strong> ist Pflicht!'.format(
            label=field.label)
      invalid_image_message = 'Sie müssen eine valide Bilddatei hochladen!'
      item_invalid_message = 'Der Wert an Stelle %(nth)s im Attribut ' \
                             '<strong><em>ATTRIBUTE</em></strong> war ungültig! ' \
                             'Daher wurde das gesamte Attribut zurückgesetzt. Hinweis:'
      ArrayField.default_error_messages['item_invalid'] = item_invalid_message
      unique_message = 'Es existiert bereits ein Datensatz mit dem angegebenen Wert im Attribut ' \
                       '<strong><em>{label}</em></strong>!'.format(label=field.label)
      field.error_messages = {
        'invalid_image': invalid_image_message,
        'required': required_message,
        'unique': unique_message
      }

  def clean_foto(self):
    """
    bereinigt Feld mit Foto
    (Hinweis: Methode wird durch Django ignoriert, falls ein solches Feld nicht existiert)

    :return: bereinigtes Feld mit Foto
    """
    if self.multi_foto_field:
      # alle weiteren Operationen nur dann durchführen,
      # wenn auch wirklich alle Pflichtfelder gefüllt sind,
      # da ansonsten die Übernahme für die weiteren Foto-Datensätze nicht funktioniert
      ok = True
      for field in self.model._meta.get_fields():
        if (
            field.name != self.model._meta.pk.name
            and field.name != 'foto'
            and self.fields[field.name].required
            and not self.data[field.name]
        ):
          ok = False
          break
      if ok:
        fotos_count = len(self.multi_files.getlist('foto'))
        if fotos_count > 1:
          i = 1
          for foto in self.multi_files.getlist('foto'):
            if i < fotos_count:
              m = self.model()
              for field in self.model._meta.get_fields():
                if field.name == 'dateiname_original':
                  setattr(m, field.name, foto.name)
                elif field.name == 'foto':
                  setattr(m, field.name, foto)
                elif field.name != m._meta.pk.name:
                  setattr(m, field.name,
                          self.cleaned_data[field.name])
              m.save()
              i += 1
    # Hinweis: Das return-Statement passt in jedem Fall,
    # also sowohl bei normalem Dateifeld als auch bei Multi-Dateifeld,
    # da hier immer die (in alphabetischer Reihenfolge des Dateinamens)
    # letzte Datei behandelt wird.
    return self.cleaned_data['foto']

  def clean_dateiname_original(self):
    """
    bereinigt Feld mit Original-Dateiname
    (Hinweis: Methode wird durch Django ignoriert, falls ein solches Feld nicht existiert)

    :return: bereinigtes Feld mit Original-Dateiname
    """
    data = self.cleaned_data['dateiname_original']
    if self.multi_foto_field and self.multi_files:
        data = self.multi_files.getlist('foto')[len(self.multi_files.getlist('foto')) - 1].name
    elif self.file:
        data = self.file.getlist('foto')[0].name
    return data

  def clean_geometrie(self):
    """
    bereinigt Feld mit Geometrie
    (Hinweis: Methode wird durch Django ignoriert, falls ein solches Feld nicht existiert)

    :return: bereinigtes Feld mit Geometrie
    """
    data = self.cleaned_data['geometrie']
    error_text = 'Es muss ein Marker in der Karte gesetzt werden bzw. eine Linie oder Fläche ' \
                 'gezeichnet werden, falls es sich um Daten linien- oder flächenhafter ' \
                 'Repräsentation handelt!'
    if (
        not self.model._meta.get_field('geometrie').blank
        and not self.model._meta.get_field('geometrie').null
        and ('EMPTY' in str(data) or '(-1188659.41326731 0)' in str(data))
    ):
      raise ValidationError(error_text)
    elif (
        self.model._meta.get_field('geometrie').blank
        and self.model._meta.get_field('geometrie').null
        and ('EMPTY' in str(data) or '(-1188659.41326731 0)' in str(data))
    ):
      return None
    else:
      return data


class DataAddView(CreateView):
  """
  erstellt ein neues Datenbankobjekt eines Datensatzes

  :param model: Datenmodell
  :param template_name: Name des Templates
  :param success_url: Success-URL
  """

  def __init__(self, model=None, template_name=None, success_url=None):
    self.model = model
    self.template_name = template_name
    self.success_url = success_url
    self.form_class = modelform_factory(
        self.model,
        form=DataForm,
        fields='__all__',
        formfield_callback=assign_widgets)
    self.multi_foto_field = None
    self.multi_files = None
    self.file = None
    super(DataAddView, self).__init__()

  def get_form_kwargs(self):
    """
    liefert **kwargs als Dictionary mit Formularattributen

    :return: **kwargs als Dictionary mit Formularattributen
    """
    kwargs = super(DataAddView, self).get_form_kwargs()
    self = set_form_attributes(self)
    if self.model.BasemodelMeta.multi_foto_field and self.request.method == 'POST':
      self.multi_files = self.request.FILES
    if self.request.method == 'POST':
      self.file = self.request.FILES
    kwargs[
        'fields_with_foreign_key_to_linkify'] = self.fields_with_foreign_key_to_linkify
    kwargs[
        'choices_models_for_choices_fields'] = self.choices_models_for_choices_fields
    kwargs[
        'group_with_users_for_choice_field'] = self.group_with_users_for_choice_field
    kwargs['multi_foto_field'] = self.model.BasemodelMeta.multi_foto_field
    kwargs['multi_files'] = self.multi_files
    kwargs['file'] = self.file
    kwargs['model'] = self.model
    kwargs['request'] = self.request
    return kwargs

  def get_context_data(self, **kwargs):
    """
    liefert Dictionary mit Kontextelementen des Views

    :param kwargs:
    :return: Dictionary mit Kontextelementen des Views
    """
    context = super(DataAddView, self).get_context_data(**kwargs)
    context = set_model_related_context_elements(context, self.model)
    context = set_form_context_elements(context, self.model)
    context['multi_foto_field'] = self.model.BasemodelMeta.multi_foto_field
    return context

  def get_initial(self):
    """
    setzt initiale Feldwerte im View

    :return: Dictionary mit initialen Feldwerten im View
    """
    ansprechpartner = None
    bearbeiter = None
    preselect_field = self.request.GET.get('preselect_field', None)
    preselect_value = self.request.GET.get('preselect_value', None)
    for field in self.model._meta.get_fields():
      if field.name == 'ansprechpartner':
        ansprechpartner = (
            self.request.user.first_name + ' '
            + self.request.user.last_name
            + ' (' + self.request.user.email.lower() + ')'
        )
      if field.name == 'bearbeiter':
        bearbeiter = (
            self.request.user.first_name + ' '
            + self.request.user.last_name
            + ' (' + self.request.user.email.lower() + ')'
        )
    if ansprechpartner or bearbeiter or (preselect_field and preselect_value):
      if not self.model.BasemodelMeta.group_with_users_for_choice_field:
        return {
            'ansprechpartner': ansprechpartner,
            'bearbeiter': bearbeiter,
            preselect_field: preselect_value
        }

  def form_valid(self, form):
    """
    sendet eine HTTP-Response, wenn Formular valide ist

    :param form: Formular, das geprüft werden soll
    :return: Success-URL als HTTP-Response, falls Formular valide
    """
    form.instance.user = self.request.user
    success(
      self.request,
      'Der neue Datensatz <strong><em>%s</em></strong> '
      'wurde erfolgreich angelegt!' % str(form.instance)
    )
    return super(DataAddView, self).form_valid(form)

  def form_invalid(self, form, **kwargs):
    """
    re-opens passed form if it is not valid
    (purpose: empty non-valid array fields)

    :param form: form
    :return: passed form if it is not valid
    """
    context_data = self.get_context_data(**kwargs)
    form.data = form.data.copy()
    for field in self.model._meta.get_fields():
      # empty all array fields
      if field.__class__.__name__ == 'ArrayField':
        form.data[field.name] = None
      # keep address reference (otherwise it would be lost on re-rendering)
      elif is_address_related_field(field):
        address = form.data.get(field.name + '_temp', None)
        form.data[field.name] = address
      # keep geometry (otherwise it would be lost on re-rendering)
      elif is_geometry_field(field.__class__):
        geometry = form.data.get(field.name, None)
        if geometry and '0,0' not in geometry and '[]' not in geometry:
          context_data['geometry'] = geometry
    context_data['form'] = form
    return self.render_to_response(context_data)


class DataChangeView(UpdateView):
  """
  ändert ein vorhandenes Datenbankobjekt eines Datensatzes

  :param model: Datenmodell
  :param template_name: Name des Templates
  :param success_url: Success-URL
  """

  def __init__(self, model=None, template_name=None, success_url=None):
    self.model = model
    self.template_name = template_name
    self.success_url = success_url
    self.form_class = modelform_factory(
      self.model,
      form=DataForm,
      fields='__all__',
      formfield_callback=assign_widgets)
    self.associated_models = None
    self.file = None
    self.associated_new = None
    self.associated_objects = None
    super(DataChangeView, self).__init__()

  def get_form_kwargs(self):
    """
    liefert **kwargs als Dictionary mit Formularattributen

    :return: **kwargs als Dictionary mit Formularattributen
    """
    kwargs = super(DataChangeView, self).get_form_kwargs()
    self = set_form_attributes(self)
    self.associated_objects = None
    self.associated_new = None
    self.associated_models = self.model.BasemodelMeta.associated_models
    if self.request.method == 'POST':
      self.file = self.request.FILES
    kwargs['associated_objects'] = self.associated_objects
    kwargs['associated_new'] = self.associated_new
    kwargs[
        'fields_with_foreign_key_to_linkify'] = self.fields_with_foreign_key_to_linkify
    kwargs[
        'choices_models_for_choices_fields'] = self.choices_models_for_choices_fields
    kwargs[
        'group_with_users_for_choice_field'] = self.group_with_users_for_choice_field
    kwargs['file'] = self.file
    kwargs['model'] = self.model
    kwargs['request'] = self.request

    # assoziierte Modelle für die Bereitstellung entsprechender Links
    # heranziehen
    if self.associated_models:
      self.associated_new = []
      self.associated_objects = []
      for associated_model in self.associated_models:
        associated_model_model = apps.get_app_config('datenmanagement').get_model(associated_model)
        associated_model_foreign_key_field = self.associated_models.get(associated_model)
        title = ''
        if associated_model_model.BasemodelMeta.object_title:
          if associated_model_model.BasemodelMeta.foreign_key_label:
            foreign_key_label = associated_model_model.BasemodelMeta.foreign_key_label
          else:
            foreign_key_label = associated_model_model._meta.verbose_name
          title = (
            sub('^[a-z]{3} ', '', associated_model_model.BasemodelMeta.object_title) +
            ' zu ' + foreign_key_label
          )
        associated_new_dict = {
            'title': title,
            'link': reverse(
                'datenmanagement:' +
                associated_model +
                '_add') +
            '?preselect_field=' +
            associated_model_foreign_key_field +
            '&preselect_value=' +
            str(
                self.object.pk)}
        self.associated_new.append(associated_new_dict)
        curr_filter = {
            associated_model_foreign_key_field: self.object.pk
        }
        for associated_object in associated_model_model.objects.filter(
                **curr_filter):
          foto = (
              associated_object.foto if hasattr(
                  associated_object,
                  'foto') else None)
          preview_img_url = ''
          preview_thumb_url = ''
          if foto:
            try:
              preview_img_url = foto.url + '?' + str(time())
              if associated_model_model.BasemodelMeta.thumbs:
                preview_thumb_url = get_thumb_url(
                    foto.url) + '?' + str(time())
            except ValueError:
              pass
          associated_object_dict = {
              'title': title,
              'name': str(associated_object),
              'id': associated_object.pk,
              'link': reverse(
                  'datenmanagement:' + associated_model + '_change',
                  args=[associated_object.pk]),
              'preview_img_url': preview_img_url,
              'preview_thumb_url': preview_thumb_url
          }
          self.associated_objects.append(associated_object_dict)
      kwargs['associated_objects'] = self.associated_objects
      kwargs['associated_new'] = self.associated_new

    return kwargs

  def get_context_data(self, **kwargs):
    """
    liefert Dictionary mit Kontextelementen des Views

    :param kwargs:
    :return: Dictionary mit Kontextelementen des Views
    """
    context = super(DataChangeView, self).get_context_data(**kwargs)
    context = set_model_related_context_elements(context, self.model)
    context = set_form_context_elements(context, self.model)
    context['associated_objects'] = (
        self.associated_objects if self.associated_objects else None)
    context['associated_new'] = (
        self.associated_new if self.associated_new else None)
    if self.model.BasemodelMeta.geometry_type:
      with connections['datenmanagement'].cursor() as cursor:
        cursor.execute(
            'SELECT st_asgeojson(st_transform(geometrie, 4326)) FROM ' +
            self.model._meta.db_table.replace('"', '') +
            ' WHERE UUID=%s;',
            [self.kwargs['pk']]
        )
        result = cursor.fetchone()[0]
        context['geometry'] = result
    else:
      context['geometry'] = None
    if self.model.BasemodelMeta.address_type:
      if self.model.BasemodelMeta.address_type == 'Adresse' and self.object.adresse:
        context['current_address'] = self.object.adresse.pk
      elif self.model.BasemodelMeta.address_type == 'Straße' and self.object.strasse:
        context['current_street'] = self.object.strasse.pk
      elif self.model.BasemodelMeta.address_type == 'Gemeindeteil' and self.object.gemeindeteil:
        context['current_district'] = self.object.gemeindeteil.pk
    # Dictionary für alle Array-Felder und deren Inhalte vorbereiten,
    # die als Inhalt mehr als einen Wert umfassen
    array_fields_values = {}
    for field in self.model._meta.get_fields():
      # bei Array-Feld...
      if field.__class__.__name__ == 'ArrayField':
        # Werte auslesen
        values = getattr(self.model.objects.get(pk=self.object.pk), field.name)
        # sofern dieses mehr als einen Wert umfasst...
        if values is not None and len(values) > 1:
          # Liste für dieses Feld aus allen Array-Inhalten ab dem zweiten zusammenstellen
          array_field_values = values[1:]
          # falls Basisfeld des Array-Felds vom Typ Datum ist...
          if field.base_field.__class__.__name__ == 'DateField':
            # Listeninhalte formatieren
            cleaned_array_field_values = []
            for array_field_value in array_field_values:
              cleaned_array_field_values.append(array_field_value.strftime('%Y-%m-%d'))
            array_field_values = cleaned_array_field_values
          # Liste in vorbereitetes Dictionary einfügen
          array_fields_values[field.name] = array_field_values
    # neuen Kontext anlegen und Dictionary für alle Array-Felder und deren Inhalte
    # dort JSON-serialisiert einfügen, die als Inhalt mehr als einen Wert umfassen
    context['array_fields_values'] = dumps(array_fields_values)
    return context

  def get_initial(self):
    """
    setzt initiale Feldwerte im View

    :return: Dictionary mit initialen Feldwerten im View
    """
    # leeres Dictionary für initiale Feldwerte im View definieren
    curr_dict = {}
    # falls Adresse, Straße oder Gemeindeteil existiert...
    if self.model.BasemodelMeta.address_type:
      # Dictionary um entsprechenden initialen Feldwert
      # für Adresse, Straße oder Gemeindeteil ergänzen
      if self.model.BasemodelMeta.address_type == 'Adresse' and self.object.adresse:
        curr_dict['adresse'] = self.object.adresse
      elif self.model.BasemodelMeta.address_type == 'Straße' and self.object.strasse:
        curr_dict['strasse'] = self.object.strasse
      elif self.model.BasemodelMeta.address_type == 'Gemeindeteil' and self.object.gemeindeteil:
        curr_dict['gemeindeteil'] = self.object.gemeindeteil
    for field in self.model._meta.get_fields():
      # bei Array-Feld...
      if field.__class__.__name__ == 'ArrayField':
        values = getattr(self.model.objects.get(pk=self.object.pk), field.name)
        # sofern dieses nicht leer ist...
        if values is not None and len(values) > 0 and values[0] is not None:
          # initialen Wert für dieses Feld auf ersten Wert des Arrays des Objektes setzen
          initial_value = values[0]
          # Dictionary um den initialen Wert für dieses Feld ergänzen
          curr_dict[field.name] = initial_value
    return curr_dict

  def form_valid(self, form):
    """
    sendet eine HTTP-Response, wenn Formular valide ist

    :param form: Formular, das geprüft werden soll
    :return: Success-URL als HTTP-Response, falls Formular valide
    """
    form.instance.user = self.request.user
    success(
      self.request,
      'Der Datensatz <strong><em>%s</em></strong> '
      'wurde erfolgreich geändert!' % str(form.instance)
    )
    return super(DataChangeView, self).form_valid(form)

  def form_invalid(self, form, **kwargs):
    """
    re-opens passed form if it is not valid
    (purpose: reset non-valid array fields to their initial state)

    :param form: form
    :return: passed form if it is not valid
    """
    context_data = self.get_context_data(**kwargs)
    form.data = form.data.copy()
    for field in self.model._meta.get_fields():
      # reset all array fields to their initial state
      if field.__class__.__name__ == 'ArrayField':
        values = getattr(self.model.objects.get(pk=self.object.pk), field.name)
        if values is not None and len(values) > 0 and values[0] is not None:
          form.data[field.name] = values[0]
        else:
          form.data[field.name] = values
      # keep address reference (otherwise it would be lost on re-rendering)
      elif is_address_related_field(field):
        address = form.data.get(field.name + '_temp', None)
        form.data[field.name] = address
      # keep geometry (otherwise it would be lost on re-rendering)
      elif is_geometry_field(field.__class__):
        geometry = form.data.get(field.name, None)
        if geometry and '0,0' not in geometry and '[]' not in geometry:
          context_data['geometry'] = geometry
    context_data['form'] = form
    return self.render_to_response(context_data)

  def get_object(self, *args, **kwargs):
    """
    liefert Objekt zurück, das geändert werden soll;
    bei fehlenden Rechten wird PermissionDenied()-Exeption geworfen

    :param args:
    :param kwargs:
    :return: Objekt, das geändert werden soll
    """
    obj = super(DataChangeView, self).get_object(*args, **kwargs)
    return obj


class DataDeleteView(SuccessMessageMixin, DeleteView):
  """
  löscht ein vorhandenes Datenbankobjekt eines Datensatzes
  """

  def get_context_data(self, **kwargs):
    """
    liefert Dictionary mit Kontextelementen des Views

    :param kwargs:
    :return: Dictionary mit Kontextelementen des Views
    """
    context = super(DataDeleteView, self).get_context_data(**kwargs)
    context['model_verbose_name_plural'] = self.model._meta.verbose_name_plural
    return context

  def get_object(self, *args, **kwargs):
    """
    liefert Objekt zurück, das gelöscht werden soll;
    bei fehlenden Rechten wird PermissionDenied()-Exeption geworfen

    :param args:
    :param kwargs:
    :return: Objekt, das gelöscht werden soll
    """
    obj = super(DataDeleteView, self).get_object(*args, **kwargs)
    userperm_delete = self.request.user.has_perm(
        'datenmanagement.delete_' + self.model.__name__.lower())
    if not userperm_delete:
      raise PermissionDenied()
    return obj

  def form_valid(self, form):
    """
    sendet eine HTTP-Response, wenn Formular valide ist

    :param form: Formular, das geprüft werden soll
    :return: Success-URL als HTTP-Response, falls Formular valide
    """
    success(
      self.request,
      'Der Datensatz <strong><em>%s</em></strong> '
      'wurde erfolgreich gelöscht!' % str(self.object)
    )
    return super(DataDeleteView, self).form_valid(form)
