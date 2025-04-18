from django.contrib.auth.models import Group, User
from django.test import TestCase, override_settings
from django.urls import reverse

from antragsmanagement.constants_vars import ADMINS, AUTHORITIES, REQUESTERS
from antragsmanagement.models import Codelist, Request, Requester
from bemas.tests.functions import clean_object_filter, get_object

from .constants_vars import DATABASES, PASSWORD, USERNAME
from .functions import login


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class DefaultTestCase(TestCase):
  """
  abstract test class
  """

  databases = DATABASES

  def init(self):
    self.test_antragsmanagement_requester_group = Group.objects.create(name=REQUESTERS)
    self.test_antragsmanagement_authority_group = Group.objects.create(name=AUTHORITIES[0])
    self.test_antragsmanagement_admin_group = Group.objects.create(name=ADMINS)
    self.test_user = User.objects.create_user(username=USERNAME, password=PASSWORD)


class DefaultModelTestCase(DefaultTestCase):
  """
  abstract test class for models
  """

  model = None
  count = 0
  create_test_object_in_classmethod = True
  attributes_values_db_create, attributes_values_db_update = {}, {}
  test_object = None

  @classmethod
  def setUpTestData(cls):
    if cls.create_test_object_in_classmethod:
      cls.test_object = cls.model.objects.create(**cls.attributes_values_db_create)

  def init(self):
    super().init()

  def generic_existance_test(self, test_object):
    """
    tests general existance of passed test object

    :param self
    :param test_object: test object
    """
    # actual number of objects equals expected number of objects?
    self.assertEqual(self.model.objects.only('pk').all().count(), self.count + 1)
    # on creation: object created exactly as it should have been created?
    # on update: object updated exactly as it should have been updated?
    self.assertEqual(test_object, self.test_object)

  def generic_create_test(self):
    """
    tests creation of test object of passed model

    :param self
    """
    # clean object filter
    object_filter = clean_object_filter(self.attributes_values_db_create)
    # get object by object filter
    test_object = get_object(self.model, object_filter)
    # test general existance of object
    self.generic_existance_test(test_object)
    # created object contains specific value in one of its fields?
    self.assertEqual(self.model.objects.only('pk').filter(**object_filter).count(), 1)

  def generic_update_test(self):
    """
    tests update of test object of passed model

    :param self
    """
    for key in self.attributes_values_db_update:
      setattr(self.test_object, key, self.attributes_values_db_update[key])
    self.test_object.save()
    # clean object filter
    object_filter = clean_object_filter(self.attributes_values_db_update)
    # get object by object filter
    test_object = get_object(self.model, object_filter)
    # test general existance of object
    self.generic_existance_test(test_object)
    # updated object contains specific value in one of its fields?
    self.assertEqual(self.model.objects.only('pk').filter(**object_filter).count(), 1)

  def generic_delete_test(self):
    """
    tests deletion of test object of passed model

    :param self
    """
    # no more test objects left?
    self.test_object.delete()
    self.assertEqual(self.model.objects.only('pk').all().count(), self.count)


class DefaultCodelistTestCase(DefaultModelTestCase):
  """
  abstract test class for codelists
  """

  def init(self):
    super().init()

  def generic_is_codelist_test(self):
    """
    tests if model is codelist

    :param self
    """
    # model declared as codelist?
    self.assertTrue(issubclass(self.model, Codelist))


class DefaultViewTestCase(DefaultTestCase):
  """
  abstract test class for views
  """

  def init(self):
    super().init()

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def generic_view_test(
    self,
    log_in,
    antragsmanagement_requester,
    antragsmanagement_authority,
    antragsmanagement_admin,
    view_name,
    view_args,
    status_code,
    content_type,
    string,
  ):
    """
    tests a view via GET

    :param self
    :param log_in: authenticate test user?
    :param antragsmanagement_requester: assign Antragsmanagement requester permissions to user?
    :param antragsmanagement_authority: assign Antragsmanagement authority permissions to user?
    :param antragsmanagement_admin: assign Antragsmanagement admin permissions to user?
    :param view_name: name of the view
    :param view_args: arguments (i.e. URL parameters) for the view
    :param status_code: expected status code of response
    :param content_type: expected content type of response
    :param string: specific string that should be contained in response
    """
    # authenticate test user
    if log_in:
      login(
        self, antragsmanagement_requester, antragsmanagement_authority, antragsmanagement_admin
      )
    # prepare the GET
    if view_args:
      url = reverse(viewname='antragsmanagement:' + view_name, kwargs=view_args)
    else:
      url = reverse('antragsmanagement:' + view_name)
    # try GETting the view
    response = self.client.get(url)
    # status code of response as expected?
    self.assertEqual(response.status_code, status_code)
    # content type of response as expected?
    self.assertEqual(response['content-type'].lower(), content_type)
    # specific string contained in response?
    if string:
      self.assertIn(string, str(response.content))


class DefaultAnonymousViewTestCase(DefaultTestCase):
  """
  abstract test class for anonymous views
  """

  def init(self):
    super().init()

  def generic_view_test(self, view_name, view_args, status_code, content_type, string):
    """
    tests a view via GET

    :param self
    :param view_name: name of the view
    :param view_args: arguments (i.e. URL parameters) for the view
    :param status_code: expected status code of response
    :param content_type: expected content type of response
    :param string: specific string that should be contained in response
    """
    # prepare the GET
    if view_args:
      url = reverse(viewname='antragsmanagement:' + view_name, kwargs=view_args)
    else:
      url = reverse('antragsmanagement:' + view_name)
    # try GETting the view
    response = self.client.get(url)
    # status code of response as expected?
    self.assertEqual(response.status_code, status_code)
    # content type of response as expected?
    self.assertEqual(response['content-type'].lower(), content_type)
    # specific string contained in response?
    if string:
      self.assertIn(string, str(response.content))


class DefaultFormViewTestCase(DefaultModelTestCase):
  """
  abstract test class for form views
  """

  def init(self):
    super().init()

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def generic_form_view_get_test(
    self,
    log_in,
    update_mode,
    antragsmanagement_requester,
    antragsmanagement_authority,
    antragsmanagement_admin,
    view_name,
    status_code,
    content_type,
    string,
  ):
    """
    tests a form view via GET

    :param self
    :param log_in: authenticate test user?
    :param update_mode: update mode?
    :param antragsmanagement_requester: assign Antragsmanagement requester permissions to user?
    :param antragsmanagement_authority: assign Antragsmanagement authority permissions to user?
    :param antragsmanagement_admin: assign Antragsmanagement admin permissions to user?
    :param view_name: name of the view
    :param status_code: expected status code of response
    :param content_type: expected content type of response
    :param string: specific string that should be contained in response
    """
    # authenticate test user
    if log_in:
      login(
        self, antragsmanagement_requester, antragsmanagement_authority, antragsmanagement_admin
      )
    # for update mode: get primary key of last object
    last_pk = self.model.objects.only('pk').last().pk
    # set URL
    if update_mode or 'delete' in view_name:
      url = reverse(viewname='antragsmanagement:' + view_name, kwargs={'pk': last_pk})
    elif 'authorative_create' in view_name or 'requestcomment_create' in view_name:
      url = reverse(viewname='antragsmanagement:' + view_name, kwargs={'request_id': last_pk})
    else:
      url = reverse('antragsmanagement:' + view_name)
    # try GETting the view
    response = self.client.get(url)
    # status code of response as expected?
    self.assertEqual(response.status_code, status_code)
    # content type of response as expected?
    self.assertEqual(response['content-type'].lower(), content_type)
    # specific string contained in response?
    if string:
      self.assertIn(string, str(response.content))

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  @override_settings(MESSAGE_STORAGE='django.contrib.messages.storage.cookie.CookieStorage')
  def generic_form_view_post_test(
    self,
    log_in,
    update_mode,
    antragsmanagement_requester,
    antragsmanagement_authority,
    antragsmanagement_admin,
    view_name,
    object_filter,
    count,
    status_code,
    content_type,
    string,
    session_variables,
  ):
    """
    tests a form view via POST

    :param self
    :param log_in: authenticate test user?
    :param update_mode: update mode?
    :param antragsmanagement_requester: assign Antragsmanagement requester permissions to user?
    :param antragsmanagement_authority: assign Antragsmanagement authority permissions to user?
    :param antragsmanagement_admin: assign Antragsmanagement admin permissions to user?
    :param view_name: name of the view
    :param object_filter: object filter
    :param count: expected number of objects passing the object filter
    :param status_code: expected status code of response
    :param content_type: expected content type of response
    :param string: specific string that should be contained in response
    :param session_variables: additional session variables
    """
    # authenticate test user
    if log_in:
      login(
        self, antragsmanagement_requester, antragsmanagement_authority, antragsmanagement_admin
      )
    # in case of request: connect test user to its requester object
    if issubclass(self.model, Request):
      requester = Requester.objects.last()
      if requester:
        requester.user_id = self.test_user.pk
        requester.save()
    # for update mode: get primary key of last object
    last_pk = self.model.objects.only('pk').last().pk
    # set URL
    if update_mode or 'delete' in view_name:
      url = reverse(viewname='antragsmanagement:' + view_name, kwargs={'pk': last_pk})
    elif 'authorative_create' in view_name or 'requestcomment_create' in view_name:
      url = reverse(
        viewname='antragsmanagement:' + view_name,
        kwargs={'request_id': session_variables['request_id']},
      )
    else:
      url = reverse('antragsmanagement:' + view_name)
    data = object_filter
    # set additional session variables
    if session_variables:
      session = self.client.session
      for key, value in session_variables.items():
        session[key] = value
      session.save()
    # try POSTing the view
    response = self.client.post(url, data)
    # status code of response as expected?
    self.assertEqual(response.status_code, status_code)
    # content type of response as expected?
    self.assertEqual(response['content-type'].lower(), content_type)
    # specific string contained in response?
    if string:
      self.assertIn(string, str(response.content))
    # clean object filter
    object_filter = clean_object_filter(object_filter, self.model)
    # number of objects passing the object filter as expected?
    if update_mode:
      self.assertEqual(self.model.objects.only('pk').filter(pk=last_pk).count(), count)
    else:
      self.assertEqual(self.model.objects.only('pk').filter(**object_filter).count(), count)
