from datetime import date
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.forms.fields import PointField, PolygonField
from django.forms import ModelForm, ValidationError
from django.forms.fields import EmailField

from antragsmanagement.constants_vars import MANAGEDAREAS_WFS_SEARCH_ELEMENT, \
  SCOPE_WFS_SEARCH_ELEMENT, SCOPE_WFS_SEARCH_STRING
from antragsmanagement.models import GeometryObject, CodelistRequestStatus, Requester
from antragsmanagement.utils import get_authorities_from_managed_areas_wfs, \
  get_corresponding_antragsmanagement_authorities, get_corresponding_requester
from toolbox.constants_vars import email_message
from toolbox.utils import find_in_wfs_features, get_overlapping_area, \
  group_dict_by_key_and_sum_values, intersection_with_wfs


#
# general objects
#

class ObjectForm(ModelForm):
  """
  generic form for instances of general objects

  :param required_css_class: CSS class for required field
  """

  required_css_class = 'required'

  def __init__(self, *args, **kwargs):
    self.user = kwargs.pop('user', None)
    kwargs.setdefault('label_suffix', '')
    super().__init__(*args, **kwargs)
    # customize messages
    for field in self.fields.values():
      text = 'Das Attribut <strong><em>{}</em></strong> ist Pflicht!'.format(field.label)
      field.error_messages['required'] = text
      if issubclass(field.__class__, EmailField):
        field.error_messages['invalid'] = email_message
      elif issubclass(field.__class__, PointField) or issubclass(field.__class__, PolygonField):
        field.error_messages['required'] = None
        if issubclass(field.__class__, PointField):
          text = 'Marker für <strong><em>{}</em></strong> muss in Karte gesetzt werden!'.format(
            field.label)
        else:
          text = '<strong><em>{}</em></strong> muss in Karte gezeichnet werden!'.format(
            field.label)
        field.error_messages['invalid_geom'] = text
        field.error_messages['invalid_geom_type'] = text

  def clean_comment(self):
    """
    cleans specific field
    """
    status = self.cleaned_data.get('status')
    comment = self.cleaned_data.get('comment')
    if status and status == CodelistRequestStatus.get_status_rejected() and not comment:
      text = 'Bei Status <strong><em>{}</em></strong>'.format(status)
      text += ' muss <strong><em>{}</em></strong> zwingend angegeben werden!'.format(
        self._meta.model._meta.get_field('comment').verbose_name)
      raise ValidationError(text)
    return comment

  def clean(self):
    """
    cleans fields
    """
    cleaned_data = super().clean()
    # if object class contains geometry:
    # clean geometry fields
    if issubclass(self._meta.model, GeometryObject):
      geometry_field = self._meta.model.BaseMeta.geometry_field
      geometry = cleaned_data.get(geometry_field)
      # fail if geometry is empty
      if '(0 0)' in str(geometry):
        text = 'Marker für <strong><em>{}</em></strong> muss in Karte gesetzt werden!'.format(
          self._meta.model._meta.get_field(geometry_field).verbose_name)
        raise ValidationError(text)
      elif geometry:
        # intersect geometry with scope
        # (check geometries only which ought to lie in scope)
        if self._meta.model.BaseMeta.geometry_in_scope:
          scope_intersections = False
          # check if geometry generally intersects with any geometry of the scope resource
          intersections = intersection_with_wfs(
            geometry=GEOSGeometry(geometry),
            wfs_config=settings.ANTRAGSMANAGEMENT_SCOPE_WFS
          )
          if intersections:
            # check if geometry intersects with scope
            scope_intersections = find_in_wfs_features(
              string=SCOPE_WFS_SEARCH_STRING,
              search_element=SCOPE_WFS_SEARCH_ELEMENT,
              wfs_features=intersections
            )
          # fail if geometry lies out of scope
          if not scope_intersections:
            text = '<strong><em>{}</em></strong> darf nicht außerhalb Rostocks liegen!'.format(
              self._meta.model._meta.get_field(geometry_field).verbose_name)
            raise ValidationError(text)
        # intersect geometry with managed areas
        # (check geometries only which ought to intersect managed areas)
        if self._meta.model.BaseMeta.geometry_in_managed_areas:
          geos_geometry = GEOSGeometry(geometry)
          # check if geometry generally intersects with any geometry of the managed areas resource
          intersections = intersection_with_wfs(
            geometry=geos_geometry,
            wfs_config=settings.ANTRAGSMANAGEMENT_MANAGEDAREAS_WFS
          )
          if intersections:
            # get overlapping areas
            overlapping_areas = []
            for intersection in intersections:
              intersection_geometry = intersection.get('geometry')
              if intersection_geometry.get('type') == 'GeometryCollection':
                for sub_geometry in intersection_geometry.get('geometries'):
                  geos_intersection_geometry = GEOSGeometry(str(sub_geometry))
                  overlapping_area = get_overlapping_area(
                    area_a=geos_geometry,
                    area_b=geos_intersection_geometry,
                    entity_value=intersection.get('properties').get(MANAGEDAREAS_WFS_SEARCH_ELEMENT)
                  )
                  overlapping_areas.append(overlapping_area)
              else:
                geos_intersection_geometry = GEOSGeometry(str(intersection_geometry))
                overlapping_area = get_overlapping_area(
                  area_a=geos_geometry,
                  area_b=geos_intersection_geometry,
                  entity_value=intersection.get('properties').get(MANAGEDAREAS_WFS_SEARCH_ELEMENT)
                )
                overlapping_areas.append(overlapping_area)
            # group overlapping areas by entity key and sum area values for each entity
            sums_overlapping_areas = group_dict_by_key_and_sum_values(
              curr_dict=overlapping_areas, group_key='entity', sum_value='area')
            # hold the main entity (i.e. the entity with the max sum)
            main_entity = max(sums_overlapping_areas, key=sums_overlapping_areas.get)
            # check if geometry intersects with managed areas of Antragsmanagement authorities
            authorities = get_authorities_from_managed_areas_wfs(
              search_element=MANAGEDAREAS_WFS_SEARCH_ELEMENT,
              wfs_features=intersections
            )
            responsibilities = get_corresponding_antragsmanagement_authorities(authorities)
            if responsibilities:
              request_responsibilities = cleaned_data.get('cleanupevent_request').responsibilities
              # clear responsibilities first
              request_responsibilities.clear()
              # add Antragsmanagement authorities as responsibilities to corresponding request
              for responsibility in responsibilities:
                main = True if responsibility.name == main_entity else False
                request_responsibilities.add(responsibility, through_defaults={'main': main})
            # fail if geometry does not intersect with at least one managed area
            # of Antragsmanagement authorities
            else:
              text = '<strong><em>{}</em></strong> muss mindestens eine Fläche'.format(
                self._meta.model._meta.get_field(geometry_field).verbose_name)
              text += ' schneiden, die durch eine am Antragsmanagement beteiligte Behörde'
              text += ' bewirtschaftet wird!'
              raise ValidationError(text)
          # fail if geometry lies outside of managed areas
          else:
            text = '<strong><em>{}</em></strong> muss mindestens eine Fläche'.format(
              self._meta.model._meta.get_field(geometry_field).verbose_name)
            text += ' des städtischen Bewirtschaftungskatasters schneiden'
            text += ' (siehe Flächendarstellungen in Karte)!'
            raise ValidationError(text)
      else:
        cleaned_data[geometry_field] = geometry
    return cleaned_data


class RequesterForm(ObjectForm):
  """
  form for creating or updating an instance of general object:
  requester (Antragsteller:in)
  """

  def clean_last_name(self):
    """
    cleans specific field
    """
    organization = self.cleaned_data.get('organization')
    first_name = self.cleaned_data.get('first_name')
    last_name = self.cleaned_data.get('last_name')
    if not organization and not first_name and not last_name:
      text = '<strong><em>{}</em></strong> muss gesetzt sein,'.format(
        self._meta.model._meta.get_field('organization').verbose_name)
      text += ' wenn <em>{}</em> und <em>{}</em> nicht gesetzt sind!'.format(
        self._meta.model._meta.get_field('first_name').verbose_name,
        self._meta.model._meta.get_field('last_name').verbose_name)
      text += ' <strong><em>{}</em></strong> und <strong><em>{}</em></strong>'.format(
        self._meta.model._meta.get_field('first_name').verbose_name,
        self._meta.model._meta.get_field('last_name').verbose_name)
      text += ' müssen gesetzt sein, wenn <em>{}</em> nicht gesetzt ist!'.format(
        self._meta.model._meta.get_field('organization').verbose_name)
      raise ValidationError(text)
    elif (not first_name and last_name) or (first_name and not last_name):
      text = '<strong><em>{}</em></strong> und <strong><em>{}</em></strong>'.format(
        self._meta.model._meta.get_field('first_name').verbose_name,
        self._meta.model._meta.get_field('last_name').verbose_name)
      text += ' müssen immer gemeinsam gesetzt sein!'
      raise ValidationError(text)
    return last_name


class RequestForm(ObjectForm):
  """
  form for instances of general object:
  request (Antrag)
  """

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # limit the status field queryset to exactly one entry (= default status)
    self.fields['status'].queryset = CodelistRequestStatus.get_status_new(as_queryset=True)
    # limit the requester field queryset to exactly one entry (= user)
    user = get_corresponding_requester(self.user, only_primary_key=False)
    self.fields['requester'].queryset = user if user else Requester.objects.none()


class RequestFollowUpForm(ObjectForm):
  """
  form for follow-up instances of general object:
  request (Antrag)
  """

  def __init__(self, *args, **kwargs):
    self.request_field = kwargs.pop('request_field', None)
    self.request_object = kwargs.pop('request_object', None)
    super().__init__(*args, **kwargs)
    # limit the request field queryset to exactly one entry (= corresponding request)
    if self.request_field and self.request_object:
      self.fields[self.request_field].queryset = self.request_object


#
# objects for request type:
# clean-up events (Müllsammelaktionen)
#

class CleanupEventEventForm(RequestFollowUpForm):
  """
  form for creating or updating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  event (Aktion)
  """

  def clean_to_date(self):
    """
    cleans specific field
    """
    from_date = self.cleaned_data.get('from_date')
    to_date = self.cleaned_data.get('to_date')
    # to_date must either be later than from_date
    # or omitted if the action is to take place on just one day
    if from_date and to_date and to_date <= from_date:
      text = '<strong><em>{}</em></strong> muss nach <em>{}</em> liegen!'.format(
        self._meta.model._meta.get_field('to_date').verbose_name,
        self._meta.model._meta.get_field('from_date').verbose_name)
      text += ' <em>{}</em> weglassen, falls Aktion an nur einem Tag stattfinden soll.'.format(
        self._meta.model._meta.get_field('to_date').verbose_name)
      raise ValidationError(text)
    # from_date must not lie in past
    if from_date and from_date < date.today():
      text = '<strong><em>{}</em></strong> darf nicht in der Vergangenheit liegen!'.format(
        self._meta.model._meta.get_field('from_date').verbose_name)
      raise ValidationError(text)
    return to_date


class CleanupEventDetailsForm(RequestFollowUpForm):
  """
  form for creating or updating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  details (Detailangaben)
  """

  def clean_waste_types_annotation(self):
    """
    cleans specific field
    """
    waste_types = self.cleaned_data.get('waste_types')
    waste_types_annotation = self.cleaned_data.get('waste_types_annotation')
    # waste_types_annotation must not be emtpy if waste_types is empty
    if not waste_types and not waste_types_annotation:
      text = 'Wenn keine <strong><em>{}</em></strong> ausgewählt ist/sind,'.format(
        self._meta.model._meta.get_field('waste_types').verbose_name)
      text += ' müssen zwingend <strong><em>{}</em></strong> angegeben werden!'.format(
        self._meta.model._meta.get_field('waste_types_annotation').verbose_name)
      raise ValidationError(text)
    return waste_types_annotation


class CleanupEventContainerForm(RequestFollowUpForm):
  """
  form for creating or updating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  container (Container)
  """

  def clean_pickup_date(self):
    """
    cleans specific field
    """
    delivery_date = self.cleaned_data.get('delivery_date')
    pickup_date = self.cleaned_data.get('pickup_date')
    # pickup date must be the same as delivery date or later
    if delivery_date and pickup_date and pickup_date < delivery_date:
      text = '<strong><em>{}</em></strong> muss gleich <em>{}</em> sein'.format(
        self._meta.model._meta.get_field('pickup_date').verbose_name,
        self._meta.model._meta.get_field('delivery_date').verbose_name)
      text += ' oder nach <em>{}</em> liegen!'.format(
        self._meta.model._meta.get_field('delivery_date').verbose_name)
      raise ValidationError(text)
    # delivery date must not lie in past
    if delivery_date and delivery_date < date.today():
      text = '<strong><em>{}</em></strong> darf nicht in der Vergangenheit liegen!'.format(
        self._meta.model._meta.get_field('delivery_date').verbose_name)
      raise ValidationError(text)
    return pickup_date
