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
    abstract = True
    managed = False

  class BasemodelMeta:
    # Boolean:
    # shall this model generally be editable?
    editable = True
    # String:
    # description of this model
    description = None
    # String:
    # short name of this model
    # (only relevant for models with foreign keys; if not specified, verbose name is used)
    short_name = None
    # Boolean:
    # shall this model (i.e. its geometries) be selectable as an additional overlay layer
    # in the maps of all form views?
    as_overlay = False
    # Boolean:
    # shall the form views of this model always be rendered in mobile mode?
    forms_in_mobile_mode = False
    # Boolean:
    # shall the maps in the form views of this model enable high zoom levels?
    forms_in_high_zoom_mode = False
    # String:
    # name of the field of this model
    # whose value shall appear in drop-down list map filters in map views
    # (if not specified, first element of ``ordering`` is used)
    naming = None
    # Dictionary:
    # shall other models (as keys), each referencing this model
    # with certain foreign key fields (as values), be used to provide corresponding links
    # in the form views and in the table of the list view of this model?
    associated_models = None
    # List of strings:
    # names of those fields of this model
    # which shall be rendered as read-only in the form views of this model
    readonly_fields = None
    # Dictionary:
    # names of those fields of this model (as keys)
    # to which other models (as values) are assigned,
    # whose values are to be used to fill corresponding selection lists
    # in the form views of this model
    choices_models_for_choices_fields = None
    # String:
    # name of a group of users which shall be used to fill the contact person field selection list
    # in the form views of this model
    group_with_users_for_choice_field = None
    # List of strings:
    # names of those fields of this model
    # which shall be equipped with additional foreign key links
    # in the form views of this model
    fields_with_foreign_key_to_linkify = None
    # Dictionary:
    # names of those fields of this model (as keys)
    # which shall be equipped with additional external links (as values)
    # in the form views of this model
    catalog_link_fields = None
    # String:
    # geometry type of this model
    geometry_type = None
    # String:
    # address search class
    address_search_class = 'address_hro'
    # Boolean:
    # shall address search results be shown in their long versions?
    address_search_long_results = False
    # String:
    # address reference type of this model (i.e. address, street or district)
    address_type = None
    # Boolean:
    # shall an address reference be mandatory for this model?
    address_mandatory = False
    # Boolean:
    # shall thumbnails be created from uploaded photos for this model?
    thumbs = True
    # Boolean:
    # shall it be possible to upload multiple photos for this model?
    # if true, multiple datasets are created, i.e. one for each photo.
    multi_photos = False
    # Boolean:
    # shall an upload field for a GeoJSON file be available in the form views of this model?
    geojson_input = False
    # Boolean:
    # shall an upload field for a GPX file be available in the form views of this model?
    gpx_input = False
    # String:
    # name of the field of this model
    # which shall be equipped with a postcode assignment function
    # in the form views of this model
    postcode_assigner = None
    # Dictionary:
    # names of those fields of this model (as keys)
    # which shall appear as columns in the table of the list view of this model
    # in exactly this order, with their respective labels, i.e. column headers (as values)
    list_fields = None
    # String:
    # name of the field appearing in ``list_fields``
    # which shall be considered as an address string
    # and thus be created from the respective model fields
    list_field_with_address_string = None
    # String:
    # name of the field of this model
    # which shall be used as a fallback when address strings cannot be used
    list_field_with_address_string_fallback_field = None
    # List of strings:
    # names of those fields of this model appearing in ``list_fields``
    # whose values are of data type date and which must therefore be treated accordingly
    # for sorting in the table of the list view of this model to work
    list_fields_with_date = None
    # List of strings:
    # names of those fields of this model appearing in ``list_fields``
    # whose values are of data type datetime and which must therefore be treated accordingly
    # for sorting in the table of the list view of this model to work
    list_fields_with_datetime = None
    # List of strings:
    # names of those fields of this model appearing in ``list_fields``
    # whose values are of Decimal type and which must therefore be treated accordingly
    # for sorting in the table of the list view of this model to work
    list_fields_with_decimal = None
    # Dictionary:
    # names of those fields appearing in ``list_fields`` (as keys)
    # which are to be converted into names of foreign key fields (as values)
    # for the table of the list view so that they can also be found and displayed
    # in the referenced table of the corresponding list view
    list_fields_with_foreign_key = None
    # Dictionary:
    # details of a foreign key field of this model
    # which shall appear as an additional column in the table of the list view of this model
    list_additional_foreign_key_field = None
    # List of dictionaries:
    # properties of assignment actions
    # which shall be selectable below the table of the list view of this model
    list_actions_assign = None
    # String:
    # name of that Boolean field of this model
    # whose values (only if ``True``) shall be used as a flag for highlighting
    # both in the table of the list view of this model and in the map view of this model
    highlight_flag = None
    # Number:
    # limit for individual map feature loading steps
    # (i.e. maximum number of map features to be loaded in one step at once)
    # in the map view of this model
    map_heavy_load_limit = None
    # List of strings:
    # names of the fields of this model
    # whose values shall concatenated
    # and as such be used as the source for the map feature tooltips in the map view of this model
    # (if not specified, primary key is used)
    map_feature_tooltip_fields = None
    # Boolean:
    # shall the one-click map filters defined in the map view template
    # appear in the map view of this model?
    map_one_click_filters = False
    # List of strings:
    # names of exactly two fields of this model
    # which shall appear as a deadline map filter in the map view of this model
    # (always processed in pairs!)
    map_deadlinefilter_fields = None
    # Dictionary:
    # names of those fields of this model (as keys)
    # which shall appear as interval map filters in the map view of this model
    # in exactly this order, with their respective titles (as values)
    # (always processed in pairs!)
    map_intervalfilter_fields = None
    # Dictionary:
    # names of those fields of this model (as keys)
    # which shall appear as map filters in the map view of this model
    # in exactly this order, with their respective titles (as values)
    map_filter_fields = None
    # List of strings:
    # names of those fields of this model appearing in ``map_filter_fields``
    # which shall appear as drop-down list map filters in the map view of this model
    map_filter_fields_as_list = None
    # List of strings:
    # names of those fields of this model appearing in ``map_filter_fields``
    # which shall appear as checkbox-set map filters in the map view of this model
    # (but these must not be the fields from ``map_filter_fields``
    # which are already multiple selection fields!)
    map_filter_fields_as_checkbox = None
    # Boolean:
    # shall those fields of this model appearing in ``map_filter_fields``
    # which are of data type Boolean
    # appear as checkbox-set map filters in the map view of this model?
    map_filter_boolean_fields_as_checkbox = False
    # Dictionary:
    # name of that field of this model (as key)
    # whose specific value (as value) shall ensure that all those objects
    # that have exactly this specific value in this field
    # do not initially appear on the map in the map view of this model
    map_filter_hide_initial = None
    # List of dictionaries:
    # properties of WMS which shall be selectable as additional overlay layers
    # in the maps of the form views of this model
    additional_wms_layers = None
    # List of dictionaries:
    # properties of WFS which shall be selectable as additional overlay layers
    # in the maps of the form views of this model
    additional_wfs_featuretypes = None


class Metamodel(Basemodel):
  """
  abstract model class for meta models
  (i.e. non-editable data models)
  """

  class Meta(Basemodel.Meta):
    abstract = True

  class BasemodelMeta(Basemodel.BasemodelMeta):
    editable = False


class Codelist(Basemodel):
  """
  abstract model class for codelists
  """

  class Meta(Basemodel.Meta):
    abstract = True


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
    abstract = True
    ordering = ['art']

  class BasemodelMeta(Codelist.BasemodelMeta):
    list_fields = {
      'art': 'Art'
    }

  def __str__(self):
    return self.art


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
    abstract = True
    ordering = ['befestigungsart']

  class BasemodelMeta(Codelist.BasemodelMeta):
    list_fields = {
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
    abstract = True
    ordering = ['material']

  class BasemodelMeta(Codelist.BasemodelMeta):
    list_fields = {
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
    abstract = True
    ordering = ['schlagwort']

  class BasemodelMeta(Codelist.BasemodelMeta):
    list_fields = {
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
    abstract = True
    ordering = ['status']

  class BasemodelMeta(Codelist.BasemodelMeta):
    list_fields = {
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
    abstract = True
    ordering = ['typ']

  class BasemodelMeta(Codelist.BasemodelMeta):
    list_fields = {
      'typ': 'Typ'
    }

  def __str__(self):
    return self.typ


#
# abstract model classes for data models
#

class SimpleModel(Basemodel):
  """
  abstract model class for simple data models
  """

  aktiv = BooleanField(
    verbose_name=' aktiv?',
    default=True
  )

  class Meta(Basemodel.Meta):
    abstract = True


class ComplexModel(SimpleModel):
  """
  abstract model class for complex data models
  """

  class Meta(SimpleModel.Meta):
    abstract = True
