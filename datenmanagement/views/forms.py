from operator import itemgetter

from django.apps import apps
from django.contrib.auth.models import Group, User
from django.contrib.gis.geos import Point
from django.contrib.postgres.fields.array import ArrayField
from django.db.models import F
from django.forms import ChoiceField, DecimalField, ModelForm, TextInput, ValidationError

from datenmanagement.models import Ansprechpartner_Baustellen

from .fields import AddressUUIDField, DistrictUUIDField, StreetUUIDField
from .functions import handle_multi_file_upload


class GenericForm(ModelForm):
  """
  generic model form
  """

  required_css_class = 'required'

  def __init__(self, *args, **kwargs):
    request = kwargs.pop('request', None)
    model = kwargs.pop('model', None)
    associated_objects = kwargs.pop('associated_objects', None)
    associated_new = kwargs.pop('associated_new', None)
    choices_models_for_choices_fields = kwargs.pop('choices_models_for_choices_fields', None)
    group_with_users_for_choice_field = kwargs.pop('group_with_users_for_choice_field', None)
    fields_with_foreign_key_to_linkify = kwargs.pop('fields_with_foreign_key_to_linkify', None)
    file = kwargs.pop('file', None)
    multi_file_upload = kwargs.pop('multi_file_upload', None)
    multi_files = kwargs.pop('multi_files', None)
    kwargs.setdefault('label_suffix', '')
    super().__init__(*args, **kwargs)
    self.request = request
    self.model = model
    self.associated_objects = associated_objects
    self.associated_new = associated_new
    self.choices_models_for_choices_fields = choices_models_for_choices_fields
    self.group_with_users_for_choice_field = group_with_users_for_choice_field
    self.fields_with_foreign_key_to_linkify = fields_with_foreign_key_to_linkify
    self.file = file
    self.multi_file_upload = multi_file_upload
    self.multi_files = multi_files
    self.address_type = self.instance.BasemodelMeta.address_type
    self.address_mandatory = self.instance.BasemodelMeta.address_mandatory
    self.geometry_coordinates_input = self.instance.BasemodelMeta.geometry_coordinates_input

    if self.model is not None:
      for field in self.model._meta.get_fields():
        # if necessary, convert text fields into selection lists
        if (
          request is not None
          and hasattr(request, 'user')
          and request.user is not None
          and (
            field.name == 'ansprechpartner'
            or field.name == 'bearbeiter'
            or field.name == 'erfasser'
          )
        ):
          if (
            self.group_with_users_for_choice_field
            and Group.objects.filter(name=self.group_with_users_for_choice_field).exists()
          ):
            users = list(
              User.objects.filter(groups__name=self.group_with_users_for_choice_field).values(
                'first_name', 'last_name', 'email'
              )
            )
            # special treatment for model Baustellen (geplant):
            # get additional users from codelist here
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
            # insert blank value on first position
            choices.insert(0, ('', '---------'))
            if field.blank and field.null:
              required = False
              initial = None
            else:
              required = True
              initial = (
                request.user.first_name
                + ' '
                + request.user.last_name
                + ' ('
                + request.user.email.lower()
                + ')'
              )
            choice_field = ChoiceField(
              required=required, label=field.verbose_name, choices=choices, initial=initial
            )
            self.fields[field.name] = choice_field
        # convert address fields to custom field types
        elif field.name == 'adresse' or field.name == 'strasse' or field.name == 'gemeindeteil':
          attrs = {
            'class': 'form-control',
            'autocapitalize': 'off',
            'autocomplete': 'off',
            'placeholder': '',
          }
          label = field.verbose_name
          required = self.address_mandatory
          if field.name == 'adresse':
            attrs['placeholder'] = 'Adresse eingeben…'
            self.fields[field.name] = AddressUUIDField(
              label=label, widget=TextInput(attrs=attrs), required=required
            )
          elif field.name == 'strasse':
            attrs['placeholder'] = 'Straße eingeben…'
            self.fields[field.name] = StreetUUIDField(
              label=label, widget=TextInput(attrs=attrs), required=required
            )
          else:
            attrs['placeholder'] = 'Gemeindeteil eingeben…'
            self.fields[field.name] = DistrictUUIDField(
              label=label, widget=TextInput(attrs=attrs), required=required
            )
        # use specific models for specific fields to fill corresponding selection lists
        elif self.choices_models_for_choices_fields:
          choices_model_name = self.choices_models_for_choices_fields.get(field.name)
          if choices_model_name is not None:
            choices_model = apps.get_app_config('datenmanagement').get_model(choices_model_name)
            oo = choices_model.objects.all()
            self.fields[field.name].choices = [(o, o) for o in oo]
      # conditionally add form fields for manually entering geometry coordinates
      if self.geometry_coordinates_input:
        x_25833_input = DecimalField(
          label='Koordinate ETRS89/UTM-33N Ostwert',
          max_value=325000,
          min_value=303000,
          max_digits=9,
          decimal_places=3,
          step_size=0.001,
        )
        x_25833_input.widget.attrs['class'] = 'form-control'
        self.fields['x_25833_input'] = x_25833_input
        y_25833_input = DecimalField(
          label='Koordinate ETRS89/UTM-33N Nordwert',
          max_value=6016000,
          min_value=5992000,
          max_digits=10,
          decimal_places=3,
          step_size=0.001,
        )
        y_25833_input.widget.attrs['class'] = 'form-control'
        self.fields['y_25833_input'] = y_25833_input
        # set geometry field to not required, otherwise saving will not be possible
        self.fields['geometrie'].required = False

    # customize messages
    for field in self.fields.values():
      if field.label == 'Geometrie':
        required_message = (
          'Es muss ein Marker in der Karte gesetzt '
          'werden bzw. eine Linie oder Fläche '
          'gezeichnet werden, falls es sich um Daten '
          'linien- oder flächenhafter Repräsentation '
          'handelt!'
        )
      else:
        required_message = 'Das Attribut <strong><em>{label}</em></strong> ist Pflicht!'.format(
          label=field.label
        )
      invalid_image_message = 'Sie müssen eine valide Bilddatei hochladen!'
      item_invalid_message = (
        'Der Wert an Stelle %(nth)s im Attribut '
        '<strong><em>ATTRIBUTE</em></strong> war ungültig! '
        'Daher wurde das gesamte Attribut zurückgesetzt. Hinweis:'
      )
      ArrayField.default_error_messages['item_invalid'] = item_invalid_message
      unique_message = (
        'Es existiert bereits ein Datensatz mit dem angegebenen Wert im Attribut '
        '<strong><em>{label}</em></strong>!'.format(label=field.label)
      )
      field.error_messages = {
        'invalid_image': invalid_image_message,
        'required': required_message,
        'unique': unique_message,
      }

  def clean_foto(self):
    """
    cleans (multi-)photo file upload field
    (note: method will be ignored by Django if such a field does not exist)

    :return: cleaned (multi-)photo file upload field
    """
    if self.multi_file_upload:
      handle_multi_file_upload(self, 'foto')
    # note:
    # the return statement is suitable in any case,
    # both for a single- and a multi-photo file upload field,
    # since the last file is always treated here (in alphabetical order of the file name)
    return self.cleaned_data['foto']

  def clean_pdf(self):
    """
    cleans (multi-)PDF file upload field
    (note: method will be ignored by Django if such a field does not exist)

    :return: (multi-)PDF file upload field
    """
    if self.multi_file_upload:
      handle_multi_file_upload(self, 'pdf')
    # note:
    # the return statement is suitable in any case,
    # both for a single- and a multi-PDF file upload field,
    # since the last file is always treated here (in alphabetical order of the file name)
    return self.cleaned_data['pdf']

  def clean_dateiname_original(self):
    """
    cleans field with original filename
    (note: method will be ignored by Django if such a field does not exist)

    :return: cleaned field with original filename
    """
    data, file_data = self.cleaned_data['dateiname_original'], None
    if self.multi_file_upload and self.multi_files:
      file_data = self.multi_files
    elif self.file:
      file_data = self.file
    if file_data:
      first_key = next(iter(file_data.keys()))
      data = file_data.getlist(first_key)[len(file_data.getlist(first_key)) - 1].name
    return data

  def clean_geometrie(self):
    """
    cleans field with geometry
    (note: method will be ignored by Django if such a field does not exist)

    :return: cleaned field with geometry
    """
    data = self.cleaned_data['geometrie']
    error_text = (
      'Es muss ein Marker in der Karte gesetzt werden bzw. eine Linie oder Fläche '
      'gezeichnet werden, falls es sich um Daten linien- oder flächenhafter '
      'Repräsentation handelt!'
    )
    if (
      not self.model._meta.get_field('geometrie').blank
      or not self.model._meta.get_field('geometrie').null
    ) and ('EMPTY' in str(data) or '(-1188659.41326731 0)' in str(data)):
      raise ValidationError(error_text)
    elif (
      self.model._meta.get_field('geometrie').blank
      and self.model._meta.get_field('geometrie').null
      and ('EMPTY' in str(data) or '(-1188659.41326731 0)' in str(data))
    ):
      return None
    else:
      return data

  def clean(self):
    """
    general field cleaning
    (always executed after all the individual field cleaning methods above)

    :return: cleaned fields
    """
    data = super().clean()
    # conditionally build geometry from form fields for manually entering geometry coordinates
    if self.geometry_coordinates_input:
      x_25833, y_25833 = data.pop('x_25833_input', None), data.pop('y_25833_input', None)
      if x_25833 is not None and y_25833 is not None and 'geometrie' in data:
        data['geometrie'] = Point((x_25833, y_25833), srid=25833)
    return data
