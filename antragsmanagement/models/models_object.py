from django.contrib.gis.db.models.fields import PointField, PolygonField
from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db.models import Index, ForeignKey, ManyToManyField, OneToOneField, CASCADE, PROTECT
from django.db.models.fields import CharField, DateField, EmailField, PositiveIntegerField, \
  TextField
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

  def save(self, *args, **kwargs):
    if self.pk is not None:
      # on every status change: send email to inform original requester
      if CleanupEventRequest.objects.get(pk=self.pk).status != self.status:
        # get corresponding Email object
        try:
          email = Email.objects.get(key='CLEANUPEVENTREQUEST_TO-REQUESTER_STATUS-CHANGED')
        except Email.DoesNotExist:
          email = None
        if email is not None:
          # set subject and body
          subject = email.subject.format(request=self.short())
          message = get_cleanupeventrequest_email_body_information(self, email.body)
          # send email
          send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.requester.email],
            fail_silently=True
          )
    super().save(*args, **kwargs)


def get_cleanupeventrequest_email_body_information(request, body):
  """
  gathers all neccessary information of passed object of model CleanupEventRequest,
  equips passed email body with it, and finally returns the equipped email body

  :param request: object of model CleanupEventRequest
  :param body: email body
  :return: email body, equipped with all neccessary information
  of passed object of model CleanupEventRequest
  """
  # if responsibilities exist
  responsibilities = '/'
  if request.responsibilities.exists():
    # use list comprehension to get authorities' short names as well as email addresses
    # and join them
    responsibilities = '\n'.join(
      [responsibility.short_contact() for responsibility in request.responsibilities.all()]
    )
  # fetch related CleanupEventEvent object
  from_date, to_date = '/', '/'
  event = CleanupEventEvent.objects.filter(cleanupevent_request=request.pk).first()
  if event:
    from_date = event.from_date.strftime('%d.%m.%Y')
    if event.to_date:
      to_date = event.to_date.strftime('%d.%m.%Y')
  # fetch related CleanupEventDetails object
  waste_quantity, waste_types, waste_types_annotation, equipments = '/', '/', '/', '/'
  details = CleanupEventDetails.objects.filter(cleanupevent_request=request.pk).first()
  if details:
    waste_quantity = str(details.waste_quantity)
    # if waste types exist
    if details.waste_types.exists():
      # use list comprehension to join waste types
      waste_types = ', '.join(
        [waste_type.name for waste_type in details.waste_types.all()]
      )
    if details.waste_types_annotation:
      waste_types_annotation = details.waste_types_annotation
    # if equipments exist
    if details.equipments.exists():
      # use list comprehension to join equipments
      equipments = ', '.join(
        [equipment.name for equipment in details.equipments.all()]
      )
  # fetch related CleanupEventContainer object
  delivery_date, pickup_date = '/', '/'
  container = CleanupEventContainer.objects.filter(cleanupevent_request=request.pk).first()
  if container:
    delivery_date = container.delivery_date.strftime('%d.%m.%Y')
    pickup_date = container.pickup_date.strftime('%d.%m.%Y')
  return body.format(
    request=request.short(),
    status=str(request.status),
    comment=request.comment if request.comment else '/',
    responsibilities=responsibilities,
    from_date=from_date,
    to_date=to_date,
    waste_quantity=waste_quantity,
    waste_types=waste_types,
    waste_types_annotation=waste_types_annotation,
    equipments=equipments,
    delivery_date=delivery_date,
    pickup_date=pickup_date
  )


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
    verbose_name='Austattung(en)',
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
