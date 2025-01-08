from django.contrib.gis.db.models.fields import PointField, PolygonField
from django.core.validators import RegexValidator
from django.db.models import Index, ForeignKey, ManyToManyField, OneToOneField, CASCADE, PROTECT, \
 UniqueConstraint, Q
from django.db.models.fields import BooleanField, CharField, DateField, EmailField, \
  PositiveIntegerField, TextField
from re import sub

from .base import Object, GeometryObject
from .models_codelist import CodelistRequestStatus, \
  CleanupEventCodelistWasteQuantity, CleanupEventCodelistWasteType, CleanupEventCodelistEquipment
from toolbox.constants_vars import standard_validators, personennamen_validators, \
  hausnummer_regex, hausnummer_message, postleitzahl_regex, postleitzahl_message, \
  rufnummer_regex, rufnummer_message
from toolbox.utils import concat_address


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
    verbose_name='E-Mail-Adresse'
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

  def short(self):
    return sub(r'.* – ', '', self.name)

  def short_contact(self):
    return self.short() + ' (' + self.email + ')'


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
  subject = CharField(
    verbose_name='Betreff',
    validators=standard_validators
  )
  body = TextField(
    verbose_name='Inhalt'
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

  user_id = PositiveIntegerField(
    verbose_name='User-ID',
    unique=True,
    blank=True,
    null=True,
    editable=False
  )
  organization = CharField(
    verbose_name='Organisation',
    blank=True,
    null=True,
    validators=standard_validators
  )
  first_name = CharField(
    verbose_name='Vorname',
    blank=True,
    null=True,
    validators=personennamen_validators
  )
  last_name = CharField(
    verbose_name='Nachname',
    blank=True,
    null=True,
    validators=personennamen_validators
  )
  email = EmailField(
    verbose_name='E-Mail-Adresse'
  )
  telephone = CharField(
    verbose_name='Telefonnummer',
    validators=[
      RegexValidator(
        regex=rufnummer_regex,
        message=rufnummer_message
      )
    ]
  )
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
    organization = self.organization if self.organization else ''
    first_name = self.first_name if self.first_name else ''
    last_name = self.last_name if self.last_name else ''
    if organization and not first_name and not last_name:
      return organization
    elif organization and first_name and last_name:
      return first_name + ' ' + last_name + ' (' + organization + ')'
    elif not organization and first_name and last_name:
      return first_name + ' ' + last_name
    else:
      return 'unbekannt'

  def address(self):
    return concat_address(self.address_street, self.address_house_number,
                          self.address_postal_code, self.address_place)

  def pseudonym(self):
    return self.organization if self.organization else '<em>Privatperson</em>'

  def verbose(self):
    verbose = str(self) + '<br>' + self.email + '<br>' + self.telephone
    verbose += '<br>' + self.address() if self.address() else ''
    return verbose


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
  comment = CharField(
    verbose_name='Statuskommentar',
    blank=True,
    null=True,
    validators=standard_validators
  )
  requester = ForeignKey(
    to=Requester,
    verbose_name='Antragsteller:in',
    on_delete=PROTECT
  )

  class Meta(Object.Meta):
    abstract = True

  def __str__(self):
    return '#' + str(self.pk) + ' vom ' + self.created.strftime('%d.%m.%Y') + \
           ' (' + str(self.status) + ')'

  def short(self):
    return '#' + str(self.pk) + ' vom ' + self.created.strftime('%d.%m.%Y')


class RequestComment(Object):
  """
  abstract model class for general object:
  request comment (Kommentar zu Antrag)
  """

  user_id = PositiveIntegerField(
    verbose_name='User-ID',
    blank=True,
    null=True,
    editable=False
  )
  content = TextField(
    verbose_name='Inhalt'
  )
  send_to_requester = BooleanField(
    verbose_name='Kommentar auch per E-Mail an Antragsteller:in senden?',
    default=False
  )

  class Meta(Object.Meta):
    abstract = True


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
    through='CleanupEventResponsibilities',
    verbose_name='Zuständigkeit(en)',
    blank=True,
    editable=False
  )

  class Meta(Request.Meta):
    db_table = 'cleanupevent_request'
    indexes = [
      Index(fields=['status']),
      Index(fields=['requester'])
    ]
    ordering = ['-id']
    verbose_name = 'Müllsammelaktion: Antrag'
    verbose_name_plural = 'Müllsammelaktionen: Anträge'

  class BaseMeta(Request.BaseMeta):
    description = 'Müllsammelaktionen: Anträge'


class CleanupEventResponsibilities(Object):
  """
  intermediary model class for many-to-many relationship
  between object for request type clean-up events (Müllsammelaktionen), request (Antrag),
  and general object, authority (Behörde)
  """

  cleanupevent_request = ForeignKey(
    to=CleanupEventRequest,
    on_delete=CASCADE
  )
  authority = ForeignKey(
    to=Authority,
    on_delete=CASCADE
  )
  main = BooleanField()

  class Meta(Request.Meta):
    db_table = 'cleanupevent_responsibilities'
    constraints = [
      UniqueConstraint(
        fields=['cleanupevent_request', 'authority'],
        name='unique_cleanupevent_request_authority'
      ),
      UniqueConstraint(
        fields=['cleanupevent_request'],
        condition=Q(main=True),
        name='unique_cleanupevent_request_main_when_main_true'
      )
    ]
    ordering = ['cleanupevent_request', 'authority', 'main']


class CleanupEventEvent(GeometryObject):
  """
  model class for object for request type clean-up events (Müllsammelaktionen):
  event (Aktion)
  """

  cleanupevent_request = OneToOneField(
    to=CleanupEventRequest,
    verbose_name='Antrag',
    on_delete=CASCADE
  )
  from_date = DateField(
    verbose_name='Startdatum/Datum'
  )
  to_date = DateField(
    verbose_name='Enddatum',
    blank=True,
    null=True
  )
  area = PolygonField(
    verbose_name='Fläche für Müllsammelaktion'
  )

  class Meta(GeometryObject.Meta):
    db_table = 'cleanupevent_event'
    indexes = [
      Index(fields=['cleanupevent_request'])
    ]
    ordering = ['-cleanupevent_request']
    verbose_name = 'Müllsammelaktion: Aktionsdaten'
    verbose_name_plural = 'Müllsammelaktionen: Aktionsdaten'

  class BaseMeta(GeometryObject.BaseMeta):
    geometry_field = 'area'
    geometry_type = 'Polygon'
    geometry_in_managed_areas = True
    description = 'Müllsammelaktionen: Aktionsdaten'

  def __str__(self):
    return 'Antrag ' + str(self.cleanupevent_request)


class CleanupEventVenue(GeometryObject):
  """
  model class for object for request type clean-up events (Müllsammelaktionen):
  venue (Treffpunkt)
  """

  cleanupevent_request = OneToOneField(
    to=CleanupEventRequest,
    verbose_name='Antrag',
    on_delete=CASCADE
  )
  place = PointField(
    verbose_name='Treffpunkt für Müllsammelaktion'
  )

  class Meta(GeometryObject.Meta):
    db_table = 'cleanupevent_venue'
    indexes = [
      Index(fields=['cleanupevent_request'])
    ]
    ordering = ['-cleanupevent_request']
    verbose_name = 'Müllsammelaktion: Treffpunkt'
    verbose_name_plural = 'Müllsammelaktionen: Treffpunkte'

  class BaseMeta(GeometryObject.BaseMeta):
    geometry_field = 'place'
    geometry_type = 'Point'
    geometry_in_scope = False
    description = 'Müllsammelaktionen: Treffpunkte'

  def __str__(self):
    return 'Antrag ' + str(self.cleanupevent_request)


class CleanupEventDetails(Object):
  """
  model class for object for request type clean-up events (Müllsammelaktionen):
  details (Detailangaben)
  """

  cleanupevent_request = OneToOneField(
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
    verbose_name=' benötigte Ausstattung(en)',
    blank=True
  )

  class Meta(Object.Meta):
    db_table = 'cleanupevent_details'
    indexes = [
      Index(fields=['cleanupevent_request'])
    ]
    ordering = ['-cleanupevent_request']
    verbose_name = 'Müllsammelaktion: Detailangaben'
    verbose_name_plural = 'Müllsammelaktionen: Detailangaben'

  class BaseMeta(Object.BaseMeta):
    description = 'Müllsammelaktionen: Detailangaben'

  def __str__(self):
    return 'Antrag ' + str(self.cleanupevent_request)


class CleanupEventContainer(GeometryObject):
  """
  model class for object for request type clean-up events (Müllsammelaktionen):
  container (Container)
  """

  cleanupevent_request = OneToOneField(
    to=CleanupEventRequest,
    verbose_name='Antrag',
    on_delete=CASCADE
  )
  delivery_date = DateField(
    verbose_name='Stellungsdatum'
  )
  pickup_date = DateField(
    verbose_name='Abholdatum'
  )
  place = PointField(
    verbose_name='Containerstandort für Müllsammelaktion'
  )

  class Meta(GeometryObject.Meta):
    db_table = 'cleanupevent_container'
    indexes = [
      Index(fields=['cleanupevent_request'])
    ]
    ordering = ['-cleanupevent_request']
    verbose_name = 'Müllsammelaktion: Containerdaten'
    verbose_name_plural = 'Müllsammelaktionen: Containerdaten'

  class BaseMeta(GeometryObject.BaseMeta):
    geometry_field = 'place'
    geometry_type = 'Point'
    description = 'Müllsammelaktionen: Containerdaten'

  def __str__(self):
    return 'Antrag ' + str(self.cleanupevent_request)


class CleanupEventDump(GeometryObject):
  """
  model class for object for request type clean-up events (Müllsammelaktionen):
  dump (Müllablageplatz)
  """

  cleanupevent_request = OneToOneField(
    to=CleanupEventRequest,
    verbose_name='Antrag',
    on_delete=CASCADE
  )
  place = PointField(
    verbose_name='Müllablageplatz für Müllsammelaktion'
  )

  class Meta(GeometryObject.Meta):
    db_table = 'cleanupevent_dump'
    indexes = [
      Index(fields=['cleanupevent_request'])
    ]
    ordering = ['-cleanupevent_request']
    verbose_name = 'Müllsammelaktion: Müllablageplatz'
    verbose_name_plural = 'Müllsammelaktionen: Müllablageplätze'

  class BaseMeta(GeometryObject.BaseMeta):
    geometry_field = 'place'
    geometry_type = 'Point'
    description = 'Müllsammelaktionen: Müllablageplätze'

  def __str__(self):
    return 'Antrag ' + str(self.cleanupevent_request)


class CleanupEventRequestComment(RequestComment):
  """
  model class for object for request type clean-up events (Müllsammelaktionen):
  request comment (Kommentar zu Antrag)
  """

  cleanupevent_request = ForeignKey(
    to=CleanupEventRequest,
    verbose_name='Antrag',
    on_delete=CASCADE
  )

  class Meta(Object.Meta):
    db_table = 'cleanupevent_request_comment'
    indexes = [
      Index(fields=['cleanupevent_request'])
    ]
    ordering = ['-cleanupevent_request', '-created']
    verbose_name = 'Müllsammelaktion: Kommentar zu Antrag'
    verbose_name_plural = 'Müllsammelaktionen: Kommentare zu Anträgen'

  class BaseMeta(Object.BaseMeta):
    description = 'Müllsammelaktionen: Kommentare zu Anträgen'

  def __str__(self):
    return 'Kommentar vom ' + self.created.strftime('%d.%m.%Y') + \
           ' zu Antrag ' + str(self.cleanupevent_request)
