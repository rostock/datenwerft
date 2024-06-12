from django.contrib.gis.db.models.fields import PointField, PolygonField
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, RegexValidator
from django.db.models import ForeignKey, ManyToManyField, CASCADE, PROTECT
from django.db.models.fields import BooleanField, CharField, DateField, EmailField, TextField

from toolbox.constants_vars import standard_validators, personennamen_validators, \
  email_message, hausnummer_regex, hausnummer_message, postleitzahl_regex, postleitzahl_message, \
  rufnummer_regex, rufnummer_message
from toolbox.utils import concat_address
from .base import Object, GeometryObject
from .models_codelist import CodelistRequestStatus, CleanupEventCodelistWasteQuantity, \
  CleanupEventCodelistWasteType, CleanupEventCodelistEquipment


#
# general objects
#

class Authority(Object):
  """
  model class for general object:
  authority (Behörde)
  """

  group = CharField(
    verbose_name='Gruppe',
    editable=False
  )
  name = CharField(
    verbose_name='Bezeichnung',
    unique=True,
    editable=False
  )
  email = EmailField(
    verbose_name='E-Mail-Adresse',
    validators=[
      EmailValidator(
        message=email_message
      )
    ]
  )

  class Meta(Object.Meta):
    db_table = 'authority'
    ordering = ['name']
    verbose_name = 'Behörde'
    verbose_name_plural = 'Behörden'

  class BaseMeta(Object.BaseMeta):
    description = 'Behörden'

  def __str__(self):
    return self.name


class Email(Object):
  """
  model class for general object:
  email (E-Mail)
  """

  key = CharField(
    verbose_name='Identifikator',
    unique=True,
    editable=False
  )
  body = TextField(
    verbose_name='Inhalt',
    validators=standard_validators
  )

  class Meta(Object.Meta):
    db_table = 'email'
    ordering = ['key']
    verbose_name = 'E-Mail'
    verbose_name_plural = 'E-Mails'

  class BaseMeta(Object.BaseMeta):
    description = 'E-Mails'

  def __str__(self):
    return self.key


class Requester(Object):
  """
  model class for general object:
  requester (Antragsteller:in)
  """

  registered = BooleanField(
    verbose_name='registriert?'
  )
  organization = CharField(
    verbose_name='Organisation',
    blank=True,
    null=True,
    validators=standard_validators
  )
  first_name = CharField(
    verbose_name='Vorname',
    validators=personennamen_validators
  )
  last_name = CharField(
    verbose_name='Nachname',
    validators=personennamen_validators
  )
  email = EmailField(
    verbose_name='E-Mail-Adresse',
    validators=[
      EmailValidator(
        message=email_message
      )
    ]
  )
  telephone = CharField(
    verbose_name='Telefonnummer',
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=rufnummer_regex,
        message=rufnummer_message
      )
    ]
  ),
  address_street = CharField(
    verbose_name='Straße',
    blank=True,
    null=True,
    validators=standard_validators
  )
  address_house_number = CharField(
    verbose_name='Hausnummer',
    max_length=4,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=hausnummer_regex,
        message=hausnummer_message
      )
    ]
  )
  address_postal_code = CharField(
    verbose_name='Postleitzahl',
    max_length=5,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=postleitzahl_regex,
        message=postleitzahl_message
      )
    ]
  )
  address_place = CharField(
    verbose_name='Ort',
    blank=True,
    null=True,
    validators=standard_validators
  )

  class Meta(Object.Meta):
    db_table = 'requester'
    ordering = ['last_name', 'first_name']
    verbose_name = 'Antragsteller:in'
    verbose_name_plural = 'Antragsteller:innen'

  class BaseMeta(Object.BaseMeta):
    description = 'Antragsteller:innen'

  def __str__(self):
    name = (self.first_name + ' ' if self.first_name else '') + self.last_name
    organization = ' (' + self.organization + ')' if self.organization else ''
    return name + organization

  def address(self):
    return concat_address(self.address_street, self.address_house_number,
                          self.address_postal_code, self.address_place)


class Request(Object):
  """
  abstract model class for general object:
  request (Antrag)
  """

  status = ForeignKey(
    to=CodelistRequestStatus,
    verbose_name='Status',
    on_delete=PROTECT
  )
  requester = ForeignKey(
    to=Requester,
    verbose_name='Antragsteller:in',
    on_delete=PROTECT
  )

  class Meta(Object.Meta):
    abstract = True

  def __str__(self):
    return '#' + str(self.id) + ' vom ' + self.created.strftime('%d.%m.%Y') + \
           ' (' + str(self.status) + ')'


#
# objects for request type:
# clean-up events (Müllsammelaktionen)
#

class CleanupEventRequest(Request):
  """
  model class for object for request type clean-up events (Müllsammelaktionen):
  request (Antrag)
  """

  responsibilities = ManyToManyField(
    Authority,
    db_table='cleanupevent_responsibilities',
    verbose_name='Zuständigkeit(en)'
  )

  class Meta(Request.Meta):
    db_table = 'cleanupevent_request'
    ordering = ['-id']
    verbose_name = 'Antrag'
    verbose_name_plural = 'Anträge'

  class BaseMeta(Request.BaseMeta):
    description = 'Müllsammelaktionen: Anträge'


class CleanupEventEvent(GeometryObject):
  """
  model class for object for request type clean-up events (Müllsammelaktionen):
  event (Aktion)
  """

  cleanupevent_request = ForeignKey(
    to=CleanupEventRequest,
    verbose_name='Antrag',
    on_delete=CASCADE
  )
  from_date = DateField(
    verbose_name='vom/am'
  )
  to_date = DateField(
    verbose_name='bis',
    blank=True,
    null=True
  )
  area = PolygonField(
    verbose_name='Fläche'
  )

  class Meta(GeometryObject.Meta):
    db_table = 'cleanupevent_event'
    ordering = ['-cleanupevent_request']
    verbose_name = 'Aktion'
    verbose_name_plural = 'Aktionen'

  class BaseMeta(GeometryObject.BaseMeta):
    geometry_field = 'area'
    description = 'Müllsammelaktionen: Aktionen'


class CleanupEventVenue(GeometryObject):
  """
  model class for object for request type clean-up events (Müllsammelaktionen):
  venue (Treffpunkt)
  """

  cleanupevent_request = ForeignKey(
    to=CleanupEventRequest,
    verbose_name='Antrag',
    on_delete=CASCADE
  )
  place = PointField(
    verbose_name='Treffpunkt'
  )

  class Meta(GeometryObject.Meta):
    db_table = 'cleanupevent_venue'
    ordering = ['-cleanupevent_request']
    verbose_name = 'Treffpunkt'
    verbose_name_plural = 'Treffpunkte'

  class BaseMeta(GeometryObject.BaseMeta):
    geometry_field = 'place'
    description = 'Müllsammelaktionen: Treffpunkte'


class CleanupEventDetails(Object):
  """
  model class for object for request type clean-up events (Müllsammelaktionen):
  details (Detailangaben)
  """

  cleanupevent_request = ForeignKey(
    to=CleanupEventRequest,
    verbose_name='Antrag',
    on_delete=CASCADE
  )
  waste_quantity = ForeignKey(
    to=CleanupEventCodelistWasteQuantity,
    verbose_name='Abfallmenge',
    on_delete=PROTECT
  )
  waste_types = ManyToManyField(
    CleanupEventCodelistWasteType,
    db_table='cleanupevent_details_wastetypes',
    verbose_name='Abfallart(en)',
    blank=True
  )
  waste_types_annotation = CharField(
    verbose_name='Bemerkungen zu Abfallart(en)',
    blank=True,
    null=True,
    validators=standard_validators
  )
  equipments = ManyToManyField(
    CleanupEventCodelistEquipment,
    db_table='cleanupevent_details_equipments',
    verbose_name='Austattung(en)',
    blank=True
  )

  class Meta(Object.Meta):
    db_table = 'cleanupevent_details'
    ordering = ['-cleanupevent_request']
    verbose_name = 'Detailangabe'
    verbose_name_plural = 'Detailangaben'

  class BaseMeta(Object.BaseMeta):
    description = 'Müllsammelaktionen: Detailangaben'

  def clean(self):
    super().clean()
    if not self.waste_types.exists() and self.waste_types_annotation is None:
      raise ValidationError('Wenn keine Abfallart(en) ausgewählt ist/sind, muss stattdessen '
                            'zwingend das zugehörige Bemerkungsfeld ausgefüllt werden!')


class CleanupEventContainer(GeometryObject):
  """
  model class for object for request type clean-up events (Müllsammelaktionen):
  container (Container)
  """

  cleanupevent_request = ForeignKey(
    to=CleanupEventRequest,
    verbose_name='Antrag',
    on_delete=CASCADE
  )
  delivery_date = DateField(
    verbose_name='Stellung'
  )
  pickup_date = DateField(
    verbose_name='Abholung'
  )
  place = PointField(
    verbose_name='Standort'
  )

  class Meta(GeometryObject.Meta):
    db_table = 'cleanupevent_container'
    ordering = ['-cleanupevent_request']
    verbose_name = 'Container'
    verbose_name_plural = 'Container'

  class BaseMeta(GeometryObject.BaseMeta):
    geometry_field = 'place'
    description = 'Müllsammelaktionen: Container'
