from datetime import timedelta
from io import StringIO

from django.conf import settings
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone as tz

from bemas.models import (
  Complaint,
  Contact,
  Organization,
  Originator,
  Person,
  Sector,
  Status,
  TypeOfImmission,
)

from .base import DefaultTestCase
from .constants_vars import VALID_POINT_DB


class DeletePersonsWithoutDataTest(DefaultTestCase):
  """
  test class for command "deletepersons" without data
  """

  def setUp(self):
    self.init()

  def test_deletepersons(self):
    out = StringIO()
    call_command('deletepersons', stdout=out)
    self.assertIn('0 person(s)', out.getvalue())


class DeletePersonsWithDataTest(DefaultTestCase):
  """
  test class for command "deletepersons" with data
  """

  @classmethod
  def setUpTestData(cls):
    organization = Organization.objects.create(name='hTWrDWAO')
    person1 = Person.objects.create(last_name='xRdIIqQV')
    person2 = Person.objects.create(last_name='xgKpANFg')
    person3 = Person.objects.create(last_name='yW9NXgth')
    Contact.objects.create(organization=organization, person=person1)
    sector = Sector.objects.first()
    originator = Originator.objects.create(
      sector=sector,
      operator_organization=organization,
      description='AV3hpjCt',
      emission_point=VALID_POINT_DB,
    )
    status1 = Status.get_default_status()
    status2 = Status.get_closed_status()
    type_of_immission = TypeOfImmission.objects.first()
    complaint1 = Complaint.objects.create(
      status=status1,
      type_of_immission=type_of_immission,
      immission_point=VALID_POINT_DB,
      originator=originator,
      description='ax1mLsDb',
    )
    complaint1.complainers_persons.add(person2)
    complaint2 = Complaint.objects.create(
      status=status2,
      type_of_immission=type_of_immission,
      immission_point=VALID_POINT_DB,
      originator=originator,
      description='NadJq8ko',
    )
    complaint2.complainers_persons.add(person3)
    expired_date = tz.now() - timedelta(days=settings.BEMAS_STATUS_CHANGE_DEADLINE_DAYS + 1)
    complaint2.status_updated_at = expired_date
    complaint2.save()

  def setUp(self):
    self.init()

  @override_settings(BEMAS_DATA_CONSIDERED_OLD_AFTER_DAYS=0)
  def test_deletepersons(self):
    out = StringIO()
    call_command('deletepersons', stdout=out)
    self.assertIn('1 person(s)', out.getvalue())
