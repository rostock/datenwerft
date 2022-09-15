import re
import time

from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.forms import ChoiceField, ModelForm, \
    TextInput, ValidationError
from django.forms.models import modelform_factory
from django.urls import reverse
from django.views import generic
from guardian.core import ObjectPermissionChecker
from operator import attrgetter

from . import fields, functions



class DataForm(ModelForm):
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
        admin_group = kwargs.pop('admin_group', None)
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
        self.admin_group = admin_group
        self.multi_foto_field = multi_foto_field
        self.multi_files = multi_files
        self.file = file
        self.model = model
        self.request = request
        self.address_type = (
            self.instance._meta.address_type if hasattr(
                self.instance._meta,
                'address_type') else None)
        self.address_mandatory = (
            self.instance._meta.address_mandatory if hasattr(
                self.instance._meta, 'address_mandatory') else None)

        for field in self.model._meta.get_fields():
            if field.name == 'ansprechpartner' or field.name == 'bearbeiter':
                # Textfelder in Auswahllisten umwandeln, falls Benutzer kein
                # Admin und kein Mitglied der Gruppe von Benutzern ist,
                # die als Admin-Gruppe für dieses Datenthema gilt
                if self.group_with_users_for_choice_field and Group.objects.filter(
                        name=self.group_with_users_for_choice_field).exists() and not (
                        self.request.user.is_superuser or self.request.user.groups.filter(
                            name=self.admin_group).exists()):
                    users = sorted(User.objects.filter(
                        groups__name=self.group_with_users_for_choice_field),
                        key=attrgetter('last_name', 'first_name'))
                    choice_field = ChoiceField(
                        choices=[
                            (user.first_name +
                             ' ' +
                             user.last_name +
                             ' (' +
                             user.email.lower() +
                                ')',
                                user.first_name +
                                ' ' +
                                user.last_name +
                                ' (' +
                                user.email.lower() +
                                ')') for user in users],
                        initial=request.user.first_name +
                        ' ' +
                        request.user.last_name +
                        ' (' +
                        request.user.email.lower() +
                        ')')
                    if field.name == 'ansprechpartner':
                        self.fields[field.name] = choice_field
                    if field.name == 'bearbeiter':
                        self.fields[field.name] = choice_field
            # Adressfelder in eigenen Feldtypen umwandeln
            elif field.name == 'adresse' or field.name == 'strasse':
                attrs = {
                    'class': 'form-control',
                    'autocapitalize': 'off',
                    'autocomplete': 'off',
                    'placeholder': ''
                }
                if field.name == 'adresse':
                    attrs['placeholder']='Adresse eingeben…'
                    self.fields[field.name] = fields.AddressUUIDField(
                        label=field.verbose_name,
                        widget=TextInput(attrs=attrs),
                        required=self.address_mandatory
                    )
                elif field.name == 'strasse':
                    attrs['placeholder']='Straße eingeben…'
                    self.fields[field.name] = fields.StreetUUIDField(
                        label=field.verbose_name,
                        widget=TextInput(attrs=attrs),
                        required=self.address_mandatory
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
            unique_message = 'Es existiert bereits ein Datensatz mit dem angegebenen Wert im Attribut <strong><em>{label}</em></strong>!'.format(
                label=field.label)
            field.error_messages = {'required': required_message,
                                    'invalid_image': invalid_image_message,
                                    'unique': unique_message}


    # Hinweis: Diese Methode wird durch Django ignoriert, falls kein Feld mit
    # Namen foto existiert.
    def clean_foto(self):
        """

        :return:
        """
        if self.multi_foto_field and self.multi_foto_field:
            # alle weiteren Operationen nur durchführen, wenn auch wirklich
            # alle Pflichtfelder gefüllt sind – ansonsten klappt die Übernahme
            # für die weiteren Foto-Datensätze nämlich nicht!
            ok = True
            for field in self.model._meta.get_fields():
                if field.name != self.model._meta.pk.name and field.name != 'foto' and \
                        self.fields[field.name].required and not \
                        self.data[field.name]:
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
        # Hinweis: Das return-Statement passt in jedem Fall, das heißt bei
        # normalem Dateifeld und bei Multi-Dateifeld, da hier immer die – in
        # alphabetischer Reihenfolge des Dateinamens – letzte Datei behandelt
        # wird.
        return self.cleaned_data['foto']

    # Hinweis: Diese Methode wird durch Django ignoriert, falls kein Feld mit
    # Namen dateiname_original existiert.
    def clean_dateiname_original(self):
        """

        :return:
        """
        data = self.cleaned_data['dateiname_original']
        if self.multi_foto_field and self.multi_foto_field:
            if self.multi_files:
                data = self.multi_files.getlist('foto')[
                    len(self.multi_files.getlist('foto')) - 1].name
        else:
            if self.file:
                data = self.file.getlist('foto')[0].name
        return data

    # Hinweis: Diese Methode wird durch Django ignoriert, falls kein Feld mit
    # Namen geometrie existiert.
    def clean_geometrie(self):
        """

        :return:
        """
        data = self.cleaned_data['geometrie']
        error_text = 'Es muss ein Marker in der Karte gesetzt werden bzw. eine Linie oder Fläche gezeichnet werden, falls es sich um Daten linien- oder flächenhafter Repräsentation handelt!'
        if 'EMPTY' in str(data) or '(-1188659.41326731 0)' in str(data):
            raise ValidationError(error_text)
        return data


class DataAddView(generic.CreateView):
    """
    erstellt ein neues Datenbankobjekt eines Datensatzes
    """

    def __init__(self, model=None, template_name=None, success_url=None):
        self.model = model
        self.template_name = template_name
        self.success_url = success_url
        self.form_class = modelform_factory(self.model, form=DataForm,
                                            fields='__all__',
                                            formfield_callback=functions.assign_widgets)
        super(DataAddView, self).__init__()

    def get_form_kwargs(self):
        """
        Liefert **kwargs als Dictionary für ein Formular.

        :return: Dictionary mit Formularattributen
        """
        kwargs = super(DataAddView, self).get_form_kwargs()
        self.fields_with_foreign_key_to_linkify = (
            self.model._meta.fields_with_foreign_key_to_linkify if hasattr(
                self.model._meta,
                'fields_with_foreign_key_to_linkify') else None)
        self.choices_models_for_choices_fields = (
            self.model._meta.choices_models_for_choices_fields if hasattr(
                self.model._meta,
                'choices_models_for_choices_fields') else None)
        self.group_with_users_for_choice_field = (
            self.model._meta.group_with_users_for_choice_field if hasattr(
                self.model._meta,
                'group_with_users_for_choice_field') else None)
        self.admin_group = (
            self.model._meta.admin_group if hasattr(self.model._meta,
                                                    'admin_group') else None)
        self.multi_foto_field = (
            self.model._meta.multi_foto_field if hasattr(
                self.model._meta,
                'multi_foto_field'
            ) else None)
        self.multi_files = (
            self.request.FILES if hasattr(
                self.model._meta,
                'multi_foto_field') and self.request.method == 'POST' else None)
        self.file = (
            self.request.FILES if self.request.method == 'POST' else None)
        kwargs[
            'fields_with_foreign_key_to_linkify'] = self.fields_with_foreign_key_to_linkify
        kwargs[
            'choices_models_for_choices_fields'] = self.choices_models_for_choices_fields
        kwargs[
            'group_with_users_for_choice_field'] = self.group_with_users_for_choice_field
        kwargs['admin_group'] = self.admin_group
        kwargs['multi_foto_field'] = self.multi_foto_field
        kwargs['multi_files'] = self.multi_files
        kwargs['file'] = self.file
        kwargs['model'] = self.model
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Liefert Dictionary mit Context-Daten des Views

        :param kwargs:
        :return: Context als Dict
        """
        context = super(DataAddView, self).get_context_data(**kwargs)
        context['LEAFLET_CONFIG'] = settings.LEAFLET_CONFIG
        context['model_name'] = self.model.__name__
        context['model_name_lower'] = self.model.__name__.lower()
        context['model_verbose_name'] = self.model._meta.verbose_name
        context[
            'model_verbose_name_plural'] = self.model._meta.verbose_name_plural
        context['model_description'] = self.model._meta.description
        context['catalog_link_fields'] = (
            self.model._meta.catalog_link_fields if hasattr(
                self.model._meta, 'catalog_link_fields') else None)
        context['catalog_link_fields_names'] = (
            list(self.model._meta.catalog_link_fields.keys()) if hasattr(
                self.model._meta, 'catalog_link_fields') else None)
        context['fields_with_foreign_key_to_linkify'] = (
            self.model._meta.fields_with_foreign_key_to_linkify if hasattr(
                self.model._meta,
                'fields_with_foreign_key_to_linkify') else None)
        context['choices_models_for_choices_fields'] = (
            self.model._meta.choices_models_for_choices_fields if hasattr(
                self.model._meta,
                'choices_models_for_choices_fields') else None)
        context['address_type'] = (
            self.model._meta.address_type if hasattr(self.model._meta,
                                                     'address_type') else None)
        context['address_mandatory'] = (
            self.model._meta.address_mandatory if hasattr(
                self.model._meta, 'address_mandatory') else None)
        context['geometry_type'] = (
            self.model._meta.geometry_type if hasattr(
                self.model._meta, 'geometry_type') else None)
        context['readonly_fields'] = (
            self.model._meta.readonly_fields if hasattr(
                self.model._meta, 'readonly_fields') else None)
        context['multi_foto_field'] = (
            self.model._meta.multi_foto_field if hasattr(
                self.model._meta, 'multi_foto_field') else None)
        context['group_with_users_for_choice_field'] = (
            self.model._meta.group_with_users_for_choice_field if hasattr(
                self.model._meta,
                'group_with_users_for_choice_field') else None)
        context['admin_group'] = (
            self.model._meta.admin_group if hasattr(self.model._meta,
                                                    'admin_group') else None)
        # Zusätzliche Kartenlayer, wie z.B. Fahrradkarte
        context['additional_wms_layers'] = (
            self.model._meta.additional_wms_layers if hasattr(
                self.model._meta, 'additional_wms_layers') else None)
        # Liste aller Datensätze für die Overlay-Daten-Liste
        model_list = {}
        app_models = apps.get_app_config('datenmanagement').get_models()
        for model in app_models:
            # Aussortieren der Datensätze ohne Geometrie
            if hasattr(model._meta, 'as_overlay') and model._meta.as_overlay == True:
                model_list[model.__name__] = model._meta.verbose_name_plural
        context['model_list'] = model_list
        # GPX-Upload-Feld
        context['gpx_input'] = (
            self.model._meta.gpx_input if hasattr(
                self.model._meta,
                'gpx_input') else None)
        # Postleitzahl-Auto-Zuweisung
        context['postcode_assigner'] = (
            self.model._meta.postcode_assigner if hasattr(
                self.model._meta,
                'postcode_assigner') else None)
        return context

    def get_initial(self):
        """
        Liefert

        :return:
        """
        ansprechpartner = None
        bearbeiter = None
        preselect_field = self.request.GET.get('preselect_field', 'foobar')
        preselect_value = self.request.GET.get('preselect_value', '')
        for field in self.model._meta.get_fields():
            if field.name == 'ansprechpartner':
                ansprechpartner = (
                    self.request.user.first_name + ' '
                    + self.request.user.last_name if (
                            self.request.user.first_name and
                            self.request.user.last_name
                    ) else self.request.user.username
                ) + ' (' + self.request.user.email.lower() + ')'
            if field.name == 'bearbeiter':
                bearbeiter = self.request.user.first_name + ' ' + \
                    self.request.user.last_name if self.request.user.first_name and self.request.user.last_name else self.request.user.username
        if ansprechpartner or bearbeiter or (
                preselect_field and preselect_value):
            if self.request.user.is_superuser or (
                hasattr(
                    self.model._meta,
                    'admin_group') and self.request.user.groups.filter(
                    name=self.model._meta.admin_group).exists()) or not hasattr(
                    self.model._meta,
                    'group_with_users_for_choice_field') or not hasattr(
                        self.model._meta,
                    'admin_group'):
                return {
                    'ansprechpartner': ansprechpartner,
                    'bearbeiter': bearbeiter,
                    preselect_field: preselect_value
                }

    def form_valid(self, form):
        """
        Sendet ein HTTPResponse, wenn Formular valide ist

        :param form: Formular, welches geprüftwerden soll
        :return: Success URL als HTTPResponse, falls valide
        """
        return super(DataAddView, self).form_valid(form)


class DataChangeView(generic.UpdateView):
    """
    ändert ein vorhandenes Datenbankobjekt eines Datensatzes
    """

    def get_form_kwargs(self):
        """

        :return:
        """
        kwargs = super(DataChangeView, self).get_form_kwargs()
        self.associated_objects = None
        self.associated_new = None
        self.associated_models = (
            self.model._meta.associated_models if hasattr(
                self.model._meta,
                'associated_models') else None)
        self.fields_with_foreign_key_to_linkify = (
            self.model._meta.fields_with_foreign_key_to_linkify if hasattr(
                self.model._meta,
                'fields_with_foreign_key_to_linkify') else None)
        self.choices_models_for_choices_fields = (
            self.model._meta.choices_models_for_choices_fields if hasattr(
                self.model._meta,
                'choices_models_for_choices_fields') else None)
        self.group_with_users_for_choice_field = (
            self.model._meta.group_with_users_for_choice_field if hasattr(
                self.model._meta,
                'group_with_users_for_choice_field') else None)
        self.admin_group = (
            self.model._meta.admin_group if hasattr(self.model._meta,
                                                    'admin_group') else None)
        self.file = (
            self.request.FILES if self.request.method == 'POST' else None)
        kwargs['associated_objects'] = self.associated_objects
        kwargs['associated_new'] = self.associated_new
        kwargs[
            'fields_with_foreign_key_to_linkify'] = self.fields_with_foreign_key_to_linkify
        kwargs[
            'choices_models_for_choices_fields'] = self.choices_models_for_choices_fields
        kwargs[
            'group_with_users_for_choice_field'] = self.group_with_users_for_choice_field
        kwargs['admin_group'] = self.admin_group
        kwargs['file'] = self.file
        kwargs['model'] = self.model
        kwargs['request'] = self.request

        # assoziierte Modelle für die Bereitstellung entsprechender Links
        # heranziehen
        if self.associated_models:
            self.associated_new = []
            self.associated_objects = []
            for associated_model in self.associated_models:
                associated_model_model = apps.get_app_config(
                    'datenmanagement').get_model(associated_model)
                associated_model_foreign_key_field = self.associated_models.get(
                    associated_model)
                title = (
                    re.sub(
                        '^[a-z]{3} ',
                        '',
                        associated_model_model._meta.object_title) +
                    ' zu ' +
                    associated_model_model._meta.foreign_key_label if hasattr(
                        associated_model_model._meta,
                        'object_title'
                    ) and hasattr(
                        associated_model_model._meta,
                        'foreign_key_label'
                    ) else associated_model_model._meta.verbose_name)
                associated_new_dict = {
                    'title': title,
                    'link': reverse(
                        'datenmanagement:' +
                        associated_model +
                        'add') +
                    '?preselect_field=' +
                    associated_model_foreign_key_field +
                    '&preselect_value=' +
                    str(
                        self.object.pk)}
                self.associated_new.append(associated_new_dict)
                filter = {}
                filter[associated_model_foreign_key_field] = self.object.pk
                for associated_object in associated_model_model.objects.filter(
                        **filter):
                    foto = (
                        associated_object.foto if hasattr(
                            associated_object,
                            'foto') else None)
                    thumbs = (
                        associated_model_model._meta.thumbs if foto and hasattr(
                            associated_model_model._meta,
                            'thumbs') else None)
                    preview_img_url = ''
                    preview_thumb_url = ''
                    if foto:
                        try:
                            preview_img_url = foto.url + '?' + str(time.time())
                            if thumbs is not None and thumbs:
                                preview_thumb_url = functions.get_thumb_url(
                                    foto.url) + '?' + str(time.time())
                            else:
                                preview_thumb_url = ''
                        except ValueError:
                            pass
                    associated_object_dict = {
                        'title': title,
                        'name': str(associated_object),
                        'id': associated_object.pk,
                        'link': reverse(
                            'datenmanagement:' + associated_model + 'change',
                            args=[associated_object.pk]),
                        'preview_img_url': preview_img_url,
                        'preview_thumb_url': preview_thumb_url
                    }
                    self.associated_objects.append(associated_object_dict)
            kwargs['associated_objects'] = self.associated_objects
            kwargs['associated_new'] = self.associated_new

        return kwargs

    def __init__(self, model=None, template_name=None, success_url=None):
        self.model = model
        self.template_name = template_name
        self.success_url = success_url
        self.form_class = modelform_factory(self.model, form=DataForm,
                                            fields='__all__',
                                            formfield_callback=functions.assign_widgets)
        super(DataChangeView, self).__init__()

    def get_context_data(self, **kwargs):
        """
        Liefert Dictionary mit Context-Daten des Views

        :param kwargs:
        :return: Context als Dict
        """
        context = super(DataChangeView, self).get_context_data(**kwargs)
        context['LEAFLET_CONFIG'] = settings.LEAFLET_CONFIG
        context['model_name'] = self.model.__name__
        context['model_name_lower'] = self.model.__name__.lower()
        context['model_verbose_name'] = self.model._meta.verbose_name
        context[
            'model_verbose_name_plural'] = self.model._meta.verbose_name_plural
        context['model_description'] = self.model._meta.description
        context['catalog_link_fields'] = (
            list(self.model._meta.catalog_link_fields.items()) if hasattr(
                self.model._meta, 'catalog_link_fields') else None)
        context['catalog_link_fields_names'] = (
            list(self.model._meta.catalog_link_fields.values()) if hasattr(
                self.model._meta, 'catalog_link_fields') else None)
        context['associated_objects'] = (
            self.associated_objects if self.associated_objects else None)
        context['associated_new'] = (
            self.associated_new if self.associated_new else None)
        context['fields_with_foreign_key_to_linkify'] = (
            self.model._meta.fields_with_foreign_key_to_linkify if hasattr(
                self.model._meta,
                'fields_with_foreign_key_to_linkify') else None)
        context['choices_models_for_choices_fields'] = (
            self.model._meta.choices_models_for_choices_fields if hasattr(
                self.model._meta,
                'choices_models_for_choices_fields') else None)
        context['address_type'] = (
            self.model._meta.address_type if hasattr(self.model._meta,
                                                     'address_type') else None)
        context['address_mandatory'] = (
            self.model._meta.address_mandatory if hasattr(
                self.model._meta, 'address_mandatory') else None)
        context['geometry_type'] = (
            self.model._meta.geometry_type if hasattr(
                self.model._meta, 'geometry_type') else None)
        if hasattr(self.model._meta, 'geometry_type'):
            with connection.cursor() as cursor:
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
        context['readonly_fields'] = (
            self.model._meta.readonly_fields if hasattr(
                self.model._meta, 'readonly_fields') else None)
        context['group_with_users_for_choice_field'] = (
            self.model._meta.group_with_users_for_choice_field if hasattr(
                self.model._meta,
                'group_with_users_for_choice_field') else None)
        context['admin_group'] = (
            self.model._meta.admin_group if hasattr(self.model._meta,
                                                    'admin_group') else None)
        context['current_address'] = (
            self.object.adresse.pk if hasattr(
                self.model._meta,
                'address_type'
            ) and self.model._meta.address_type == 'Adresse' and self.object.adresse else None)
        context['current_street'] = (
            self.object.strasse.pk if hasattr(
                self.model._meta,
                'address_type') and self.model._meta.address_type == 'Straße' and self.object.strasse else None)
        context['additional_wms_layers'] = (
            self.model._meta.additional_wms_layers if hasattr(
                self.model._meta, 'additional_wms_layers') else None)
        # Hinzufügen anderer Datensätze
        model_list = {}
        app_models = apps.get_app_config('datenmanagement').get_models()
        for model in app_models:
            # Aussortieren der Datensätze ohne Geometrie
            if hasattr(model._meta,
                       'as_overlay') and model._meta.as_overlay == True:
                model_list[model.__name__] = model._meta.verbose_name
        context['model_list'] = model_list
        # GPX-Upload-Feld
        context['gpx_input'] = (
            self.model._meta.gpx_input if hasattr(
                self.model._meta,
                'gpx_input') else None)
        # Postleitzahl-Auto-Zuweisung
        context['postcode_assigner'] = (
            self.model._meta.postcode_assigner if hasattr(
                self.model._meta,
                'postcode_assigner') else None)
        return context

    def get_initial(self):
        """
        Liefert entweder Adresse oder Straße des Objektes, falls eines der
        beiden existiert. Falls nicht, wird ein leeres Dictionary zurückgegeben.

        :return: Leeres Dict oder Dict mit Adresse oder Straße.
        """
        if hasattr(self.model._meta, 'address_type'):
            if self.model._meta.address_type == 'Adresse' and \
                    self.object.adresse:
                return {'adresse': self.object.adresse}
            elif self.model._meta.address_type == 'Straße' and \
                    self.object.strasse:
                return {'strasse': self.object.strasse}
            else:
                return {}
        else:
            return {}

    def form_valid(self, form):
        return super(DataChangeView, self).form_valid(form)

    def get_object(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        obj = super(DataChangeView, self).get_object(*args, **kwargs)
        userobjperm_change = ObjectPermissionChecker(
            self.request.user).has_perm(
            'change_' + self.model.__name__.lower(), obj)
        userperm_view = self.request.user.has_perm(
            'datenmanagement.view_' + self.model.__name__.lower())
        if not userobjperm_change and not userperm_view:
            raise PermissionDenied()
        return obj


class DataDeleteView(generic.DeleteView):
    """
    löscht ein vorhandenes Datenbankobjekt eines Datensatzes
    """

    def get_object(self, *args, **kwargs):
        """
        Gibt Objekt zurück, welches gelöscht werden soll. Bei fehlenden Rechten
        wird PermissionDenied() Exeption geworfen.

        :param args:
        :param kwargs:
        :return: zu löschendes Objekt
        """
        obj = super(DataDeleteView, self).get_object(*args, **kwargs)
        userobjperm_delete = ObjectPermissionChecker(
            self.request.user).has_perm(
            'delete_' + self.model.__name__.lower(), obj)
        if not userobjperm_delete:
            raise PermissionDenied()
        return obj
