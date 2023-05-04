from django.contrib.contenttypes.models import ContentType

from toolbox.models import Subsets
from bemas.models import Complaint, Organization, Originator, Sector, Status, TypeOfImmission
from .base import DefaultViewTestCase
from .constants_vars import VALID_POINT_DB


#
# general views
#

class IndexViewTest(DefaultViewTestCase):
  """
  test class for main page
  """

  def setUp(self):
    self.init()

  def test_view_no_rights(self):
    self.generic_view_test(
      False, False, 'index', None, 200,
      'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'index', None, 200,
      'text/html; charset=utf-8', 'Codelisten'
    )


class MapViewTest(DefaultViewTestCase):
  """
  test class for map page
  """

  @classmethod
  def setUpTestData(cls):
    organization = Organization.objects.create(
      name='N1YvcbxM'
    )
    sector = Sector.objects.first()
    originator = Originator.objects.create(
      sector=sector,
      operator=organization,
      description='NutMoxfw',
      emission_point=VALID_POINT_DB
    )
    status = Status.get_default_status()
    type_of_immission = TypeOfImmission.objects.first()
    complaint = Complaint.objects.create(
      status=status,
      type_of_immission=type_of_immission,
      immission_point=VALID_POINT_DB,
      originator=originator,
      description='e506TjLt'
    )
    Subsets.objects.create(
      model=ContentType.objects.filter(
        app_label='bemas',
        model='originator'
      ).first(),
      pk_field='id',
      pk_values=[
        originator.pk
      ]
    )
    Subsets.objects.create(
      model=ContentType.objects.filter(
        app_label='bemas',
        model='complaint'
      ).first(),
      pk_field='id',
      pk_values=[
        complaint.pk
      ]
    )

  def setUp(self):
    self.init()

  def test_view_no_rights(self):
    self.generic_view_test(
      False, False, 'map', None, 200,
      'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'map', None, 200,
      'text/html; charset=utf-8', 'Immissions- und Emissionsorte'
    )

  def test_view_originator_subset_no_rights(self):
    self.generic_view_test(
      False, False, 'map_model_subset', ['originator', 1], 200,
      'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_view_originator_subset_standard_rights(self):
    self.generic_view_test(
      True, False, 'map_model_subset', ['originator', 1], 200,
      'text/html; charset=utf-8', 'Kartendaten angezeigt'
    )

  def test_view_complaint_subset_no_rights(self):
    self.generic_view_test(
      False, False, 'map_model_subset', ['complaint', 1], 200,
      'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_view_complaint_subset_standard_rights(self):
    self.generic_view_test(
      True, False, 'map_model_subset', ['complaint', 1], 200,
      'text/html; charset=utf-8', 'Kartendaten angezeigt'
    )
