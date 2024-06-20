from django.contrib.gis.db.models import Model
from django.db.models.fields import BooleanField, CharField, UUIDField
from uuid import uuid4

from toolbox.constants_vars import standard_validators


#
# base abstract model classes
#

class Basemodel(Model):
  """
  default abstract model class
  """
  uuid = UUIDField(
    primary_key=True,
    default=uuid4,
    editable=False
  )

  class Meta:
    abstract: bool = True
    managed: bool = False

  class BasemodelMeta:
    """
    This class defines soma special meta information for models.

    Attributes:
      editable: shall this model generally be editable?
      description: description of this model
      short_name: short name of this model (if foreign keys are used;
          if not specified -> verbose name)
      as_overlay: shall geometries be selectable as overlay layer in the map in all form views?
      default_overlays: list of default overlay layers in the map of form view
      forms_in_mobile_mode: shall forms for this model be in mobile mode?
      forms_in_high_zoom_mode: shall map in form view be in high zoom mode?
      forms_in_high_zoom_mode_default_aerial: shall map in form view be an aerial image,
          if high zoom mode active?
      naming: name shown in map filters drop-down menus
      readonly_fields: shall fields be read-only?
      geometry_type: type of the geometry represented by this model
      address_search_class: address search class
      address_search_long_results: shall address search results be shown in their long versions?
      address_type: type of the address represented by this model
          (i.e. address, street or district)
      address_mandatory: shall an address reference be mandatory for this model?
      thumbs: shall thumbnails be created from uploaded photos for this model?
      geojson_input: shall an upload field for a GeoJSON file be available in the form view?
      gpx_input: shall an upload field for a GPX file be available in the form view?
      associated_models: shall other models referencing this model?
      choices_models_for_choices_fields:
      group_with_users_for_choice_field:
      fields_with_foreign_key_to_linkify:
      catalog_link_fields:
      multi_photos:
      postcode_assigner:
      list_fields:
      list_field_with_address_string:
      list_field_with_address_string_fallback_field:
      list_fields_with_date:
      list_fields_with_datetime:
      list_fields_with_decimal:
      list_fields_with_foreign_key:
      list_additional_foreign_key_field:
      list_actions_assign:
      highlight_flag:
      map_heavy_load_limit:
      map_feature_tooltip_fields:
      map_one_click_filters:
      map_deadlinefilter_fields:
      map_intervalfilter_fields:
      map_filter_fields:
      map_filter_fields_as_list:
      map_filter_fields_as_checkbox:
      map_filter_boolean_fields_as_checkbox:
      map_filter_hide_initial:
      additional_wms_layers:
      additional_wfs_featuretypes:

    """
    editable: bool = True
    description: str = None
    short_name: str = None
    as_overlay: bool = False
    default_overlays: list[str] = None
    forms_in_mobile_mode: bool = False
    forms_in_high_zoom_mode: bool = False
    forms_in_high_zoom_mode_default_aerial: bool = False
    naming: str = None
    readonly_fields: list[str] = None
    geometry_type: str = None
    address_search_class: str = 'address_hro'
    address_search_long_results: bool = False
    address_type: str = None
    address_mandatory: bool = False
    thumbs: bool = True
    geojson_input: bool = False
    gpx_input: bool = False

    # shall other models (as keys), each referencing this model
    # with certain foreign key fields (as values), be used to provide corresponding links
    # in the form views and in the table of the list view of this model?
    associated_models: dict[str, str] = None

    # names of those fields of this model (as keys)
    # to which other models (as values) are assigned,
    # whose values are to be used to fill corresponding selection lists
    # in the form views of this model
    choices_models_for_choices_fields: dict[str, str] = None

    # name of a group of users which shall be used to fill the contact person field selection list
    # in the form views of this model
    group_with_users_for_choice_field: str = None

    # names of those fields of this model
    # which shall be equipped with additional foreign key links
    # in the form views of this model
    fields_with_foreign_key_to_linkify: list[str] = None

    # names of those fields of this model (as keys)
    # which shall be equipped with additional external links (as values)
    # in the form views of this model
    catalog_link_fields: dict[str, str] = None

    # shall it be possible to upload multiple photos for this model?
    # if true, multiple datasets are created, i.e. one for each photo.
    multi_photos: bool = False

    # name of the field of this model
    # which shall be equipped with a postcode assignment function
    # in the form views of this model
    postcode_assigner: str = None

    # names of those fields of this model (as keys)
    # which shall appear as columns in the table of the list view of this model
    # in exactly this order, with their respective labels, i.e. column headers (as values)
    list_fields: dict[str, str] = None

    # name of the field appearing in ``list_fields``
    # which shall be considered as an address string
    # and thus be created from the respective model fields
    list_field_with_address_string: str = None

    # name of the field of this model
    # which shall be used as a fallback when address strings cannot be used
    list_field_with_address_string_fallback_field: str = None

    # names of those fields of this model appearing in ``list_fields``
    # whose values are of data type date and which must therefore be treated accordingly
    # for sorting in the table of the list view of this model to work
    list_fields_with_date: list[str] = None

    # names of those fields of this model appearing in ``list_fields``
    # whose values are of data type datetime and which must therefore be treated accordingly
    # for sorting in the table of the list view of this model to work
    list_fields_with_datetime: list[str] = None

    # names of those fields of this model appearing in ``list_fields``
    # whose values are of Decimal type and which must therefore be treated accordingly
    # for sorting in the table of the list view of this model to work
    list_fields_with_decimal: list[str] = None

    # names of those fields appearing in ``list_fields`` (as keys)
    # which are to be converted into names of foreign key fields (as values)
    # for the table of the list view so that they can also be found and displayed
    # in the referenced table of the corresponding list view
    list_fields_with_foreign_key: dict[str, str] = None

    # details of a foreign key field of this model
    # which shall appear as an additional column in the table of the list view of this model
    list_additional_foreign_key_field: dict[str, str] = None

    # properties of assignment actions
    # which shall be selectable below the table of the list view of this model
    list_actions_assign: list[dict] = None

    # name of that Boolean field of this model
    # whose values (only if ``True``) shall be used as a flag for highlighting
    # both in the table of the list view of this model and in the map view of this model
    highlight_flag: str = None

    # limit for individual map feature loading steps
    # (i.e. maximum number of map features to be loaded in one step at once)
    # in the map view of this model
    map_heavy_load_limit: int = None

    # names of the fields of this model
    # whose values shall concatenated
    # and as such be used as the source for the map feature tooltips in the map view of this model
    # (if not specified, primary key is used)
    map_feature_tooltip_fields: list[str] = None

    # shall the one-click map filters defined in the map view template
    # appear in the map view of this model?
    map_one_click_filters: bool = False

    # names of exactly two fields of this model
    # which shall appear as a deadline map filter in the map view of this model
    # (always processed in pairs!)
    map_deadlinefilter_fields: list[str] = None

    # names of those fields of this model (as keys)
    # which shall appear as interval map filters in the map view of this model
    # in exactly this order, with their respective titles (as values)
    # (always processed in pairs!)
    map_intervalfilter_fields: dict[str, str] = None

    # names of those fields of this model (as keys)
    # which shall appear as map filters in the map view of this model
    # in exactly this order, with their respective titles (as values)
    map_filter_fields: dict[str, str] = None

    # names of those fields of this model appearing in ``map_filter_fields``
    # which shall appear as drop-down list map filters in the map view of this model
    map_filter_fields_as_list: list[str] = None

    # names of those fields of this model appearing in ``map_filter_fields``
    # which shall appear as checkbox-set map filters in the map view of this model
    # (but these must not be the fields from ``map_filter_fields``
    # which are already multiple selection fields!)
    map_filter_fields_as_checkbox: list[str] = None

    # shall those fields of this model appearing in ``map_filter_fields``
    # which are of data type Boolean
    # appear as checkbox-set map filters in the map view of this model?
    map_filter_boolean_fields_as_checkbox: bool = False

    # name of that field of this model (as key)
    # whose specific value (as value) shall ensure that all those objects
    # that have exactly this specific value in this field
    # do not initially appear on the map in the map view of this model
    map_filter_hide_initial: dict[str, str] = None

    # properties of WMS which shall be selectable as additional overlay layers
    # in the maps of the form views of this model
    additional_wms_layers: list[dict] = None

    # properties of WFS which shall be selectable as additional overlay layers
    # in the maps of the form views of this model
    additional_wfs_featuretypes: list[dict] = None


class Metamodel(Basemodel):
  """
  abstract model class for meta models
  (i.e. non-editable data models)
  """

  class Meta(Basemodel.Meta):
    abstract: bool = True

  class BasemodelMeta(Basemodel.BasemodelMeta):
    editable: bool = False


class Codelist(Basemodel):
  """
  abstract model class for codelists
  """

  class Meta(Basemodel.Meta):
    abstract: bool = True


#
# abstract model classes for specific codelists
#

class Art(Codelist):
  """
  abstract model class for 'Art' codelists
  """

  art = CharField(
    verbose_name='Art',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    abstract: bool = True
    ordering: list[str] = ['art']

  class BasemodelMeta(Codelist.BasemodelMeta):
    list_fields: dict[str, str] = {
      'art': 'Art'
    }

  def __str__(self):
    return self.art


class Ausfuehrung(Codelist):
  """
  abstract model class for 'Ausführung' codelists
  """

  ausfuehrung = CharField(
    verbose_name='Ausführung',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    abstract: bool = True
    ordering: list[str] = ['ausfuehrung']

  class BasemodelMeta(Codelist.BasemodelMeta):
    list_fields: dict[str, str] = {
      'ausfuehrung': 'Ausführung'
    }

  def __str__(self):
    return self.ausfuehrung


class Befestigungsart(Codelist):
  """
  abstract model class for 'Befestigungsart' codelists
  """

  befestigungsart = CharField(
    verbose_name='Befestigungsart',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    abstract: bool = True
    ordering: list[str] = ['befestigungsart']

  class BasemodelMeta(Codelist.BasemodelMeta):
    list_fields: dict[str, str] = {
      'befestigungsart': 'Befestigungsart'
    }

  def __str__(self):
    return self.befestigungsart


class Material(Codelist):
  """
  abstract model class for 'Material' codelists
  """

  material = CharField(
    verbose_name='Material',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    abstract: bool = True
    ordering: list[str] = ['material']

  class BasemodelMeta(Codelist.BasemodelMeta):
    list_fields: dict[str, str] = {
      'material': 'Material'
    }

  def __str__(self):
    return self.material


class Schlagwort(Codelist):
  """
  abstract model class for 'Schlagwort' codelists
  """

  schlagwort = CharField(
    verbose_name='Schlagwort',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    abstract: bool = True
    ordering: list[str] = ['schlagwort']

  class BasemodelMeta(Codelist.BasemodelMeta):
    list_fields: dict[str, str] = {
      'schlagwort': 'Schlagwort'
    }

  def __str__(self):
    return self.schlagwort


class Status(Codelist):
  """
  abstract model class for 'Status' codelists
  """

  status = CharField(
    verbose_name='Status',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    abstract: bool = True
    ordering: list[str] = ['status']

  class BasemodelMeta(Codelist.BasemodelMeta):
    list_fields: dict[str, str] = {
      'status': 'Status'
    }

  def __str__(self):
    return self.status


class Typ(Codelist):
  """
  abstract model class for 'Typ' codelists
  """

  typ = CharField(
    verbose_name='Typ',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    abstract: bool = True
    ordering: list[str] = ['typ']

  class BasemodelMeta(Codelist.BasemodelMeta):
    list_fields: dict[str, str] = {
      'typ': 'Typ'
    }

  def __str__(self):
    return self.typ


#
# abstract model classes for data models
#

class SimpleModel(Basemodel):
  """
  Class representing a simple model.

  Inherits from the Basemodel class.

  Attributes:
    aktiv (bool): Indicates if the model is active. Default is True.

  Meta:
      Inherits the Meta class from Basemodel.

  """

  aktiv = BooleanField(
    verbose_name=' aktiv?',
    default=True
  )

  class Meta(Basemodel.Meta):
    abstract: bool = True


class ComplexModel(SimpleModel):
  """
  abstract model class for complex data models
  """

  class Meta(SimpleModel.Meta):
    abstract: bool = True
