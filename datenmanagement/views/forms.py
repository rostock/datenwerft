from django.apps import apps
from django.contrib.auth.models import Group, User
from django.contrib.postgres.fields.array import ArrayField
from django.db.models import F
from django.forms import ChoiceField, ModelForm, TextInput, ValidationError
from operator import itemgetter

from datenmanagement.models import Ansprechpartner_Baustellen
from .fields import AddressUUIDField, DistrictUUIDField, StreetUUIDField


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
    multi_foto_field = kwargs.pop('multi_foto_field', None)
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
    self.multi_foto_field = multi_foto_field
    self.multi_files = multi_files
    self.address_type = self.instance.BasemodelMeta.address_type
    self.address_mandatory = self.instance.BasemodelMeta.address_mandatory

    for field in self.model._meta.get_fields():
      # if necessary, convert text fields into selection lists
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
          choice_field = ChoiceField(
            label=field.verbose_name,
            choices=choices,
            initial=request.user.first_name + ' ' + request.user.last_name +
            ' (' + request.user.email.lower() + ')'
          )
          if field.name == 'ansprechpartner' or field.name == 'bearbeiter':
            self.fields[field.name] = choice_field
      # convert address fields to custom field types
      elif field.name == 'adresse' or field.name == 'strasse' or field.name == 'gemeindeteil':
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
          self.fields[field.name] = DistrictUUIDField(
              label=label,
              widget=TextInput(attrs=attrs),
              required=required
          )
      # use specific models for specific fields to fill corresponding selection lists
      elif self.choices_models_for_choices_fields:
        choices_model_name = self.choices_models_for_choices_fields.get(field.name)
        if choices_model_name is not None:
          choices_model = apps.get_app_config('datenmanagement').get_model(choices_model_name)
          choices = []
          for choices_model_object in choices_model.objects.all():
            choices.append((choices_model_object, choices_model_object))
          self.fields[field.name].choices = choices

    # customize messages
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
    cleans field with foto
    (note: method will be ignored by Django if such a field does not exist)

    :return: cleaned field with foto
    """
    if self.multi_foto_field:
      # only carry out all further operations if all mandatory fields have been filled,
      # since otherwise the transfer for the other photo objects will not work
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
    # note: the return statement fits in every case,
    # both with a normal file field and with a multi-file field,
    # since here always the last file is handled (in alphabetical order of the file name)
    return self.cleaned_data['foto']

  def clean_dateiname_original(self):
    """
    cleans field with original filename
    (note: method will be ignored by Django if such a field does not exist)

    :return: cleaned field with original filename
    """
    data = self.cleaned_data['dateiname_original']
    if self.multi_foto_field and self.multi_files:
        data = self.multi_files.getlist('foto')[len(self.multi_files.getlist('foto')) - 1].name
    elif self.file:
        data = self.file.getlist('foto')[0].name
    return data

  def clean_geometrie(self):
    """
    cleans field with geometry
    (note: method will be ignored by Django if such a field does not exist)

    :return: cleaned field with geometry
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
