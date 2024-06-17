from django.conf import settings
from django.views.generic.base import TemplateView

from .base import ObjectCreateView, ObjectUpdateView
from .functions import add_permissions_context_elements, add_useragent_context_elements
from antragsmanagement.models import Authority, Email, Requester, CleanupEventRequest
from antragsmanagement.utils import get_corresponding_requester_pk


#
# general
#

class IndexView(TemplateView):
  """
  view for main page
  """

  template_name = 'antragsmanagement/index.html'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add user agent related context elements
    context = add_useragent_context_elements(context, self.request)
    # add permissions related context elements
    context = add_permissions_context_elements(context, self.request.user)
    # add information about corresponding requester object for user to context
    context['corresponding_requester'] = get_corresponding_requester_pk(self.request.user)
    return context


#
# general objects
#

class AuthorityUpdateView(ObjectUpdateView):
  """
  view for form page for updating an instance of general object:
  authority (Behörde)
  """

  model = Authority
  cancel_url = 'antragsmanagement:index'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add permissions related context elements:
    # set admin permissions as necessary permissions
    context = add_permissions_context_elements(
      context, self.request.user, settings.ANTRAGSMANAGEMENT_ADMIN_GROUP_NAME)
    return context


class EmailUpdateView(ObjectUpdateView):
  """
  view for form page for updating an instance of general object:
  email (E-Mail)
  """

  model = Email
  cancel_url = 'antragsmanagement:index'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add permissions related context elements:
    # set admin permissions as necessary permissions
    context = add_permissions_context_elements(
      context, self.request.user, settings.ANTRAGSMANAGEMENT_ADMIN_GROUP_NAME)
    return context


class RequesterCreateView(ObjectCreateView):
  """
  view for form page for creating an instance of general object:
  requester (Antragsteller:in)
  """

  model = Requester

  def form_valid(self, form):
    """
    sends HTTP response if passed form is valid

    :param form: form
    :return: HTTP response if passed form is valid
    """
    if self.request.user.is_authenticated:
      instance = form.save(commit=False)
      # set the value of the user_id field programmatically
      instance.user_id = self.request.user.id
    return super().form_valid(form)

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add permissions related context elements:
    # set requester permissions as necessary permissions
    context = add_permissions_context_elements(
      context, self.request.user, settings.ANTRAGSMANAGEMENT_REQUESTER_GROUP_NAME)
    return context


class RequesterUpdateView(ObjectUpdateView):
  """
  view for form page for updating an instance of general object:
  requester (Antragsteller:in)
  """

  model = Requester

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add permissions related context elements:
    # set requester permissions as necessary permissions
    context = add_permissions_context_elements(
      context, self.request.user, settings.ANTRAGSMANAGEMENT_REQUESTER_GROUP_NAME)
    return context


class CleanupEventRequestCreateView(ObjectCreateView):
  """
  view for form page for creating an instance of object for request type clean-up events
  (Müllsammelaktionen):
  request (Antrag)
  """

  model = CleanupEventRequest

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add permissions related context elements:
    # set requester permissions as necessary permissions
    context = add_permissions_context_elements(
      context, self.request.user, settings.ANTRAGSMANAGEMENT_REQUESTER_GROUP_NAME)
    return context
