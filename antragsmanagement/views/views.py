from django.conf import settings
from django.urls import reverse
from django.views.generic.base import TemplateView

from .base import ObjectCreateView, ObjectUpdateView
from .forms import RequestForm, RequestFollowUpForm
from .functions import add_permissions_context_elements, add_useragent_context_elements
from antragsmanagement.models import CodelistRequestStatus, Authority, Email, Requester, \
  CleanupEventRequest, CleanupEventEvent
from antragsmanagement.utils import get_corresponding_requester, get_request


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
    # remove any request ID in session
    self.request.session.pop('request_id', None)
    # add user agent related context elements
    context = add_useragent_context_elements(context, self.request)
    # add permissions related context elements
    context = add_permissions_context_elements(context, self.request.user)
    # add to context: information about corresponding requester object for user
    context['corresponding_requester'] = get_corresponding_requester(self.request.user)
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


class RequestFormMixin:
  """
  mixin for form page for creating or updating an instance of general object:
  request (Antrag)
  """

  template_name = 'antragsmanagement/form-request.html'
  form = RequestForm

  def get_form_kwargs(self):
    """
    returns ``**kwargs`` as a dictionary with form attributes

    :return: ``**kwargs`` as a dictionary with form attributes
    """
    kwargs = super().get_form_kwargs()
    # pass request user to form
    kwargs['user'] = self.request.user
    return kwargs

  def form_valid(self, form):
    """
    sends HTTP response if passed form is valid

    :param form: form
    :return: HTTP response if passed form is valid
    """
    # delay necessary to allow automatic field contents to populate
    request = form.save(commit=False)
    request.full_clean()
    request.save()
    # store ID of new request in session in order to pass it to next view
    self.request.session['request_id'] = request.id
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
    # add to context: information about corresponding requester object for user
    context['corresponding_requester'] = get_corresponding_requester(self.request.user)
    return context

  def get_initial(self):
    """
    conditionally sets initial field values for this view

    :return: dictionary with initial field values for this view
    """
    # set status to default status and set requester to user
    user = get_corresponding_requester(self.request.user)
    return {
      'status': CodelistRequestStatus.get_status_new(),
      'requester': user if user else Requester.objects.order_by('-id')[:1]
    }


class RequestFollowUpFormMixin:
  """
  mixin for form page for creating or updating a follow-up instance of general object:
  request (Antrag)
  """

  template_name = 'antragsmanagement/form-request-followup.html'
  form = RequestFollowUpForm

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
    # add to context: request ID passed in session
    context['corresponding_request'] = self.request.session.get('request_id', None)
    return context

  def get_initial(self):
    """
    conditionally sets initial field values for this view

    :return: dictionary with initial field values for this view
    """
    # get corresponding request object via ID passed in session
    # and set request to it
    return {
      'cleanupevent_request': get_request(
        CleanupEventRequest, self.request.session.get('request_id', None))
    }


#
# objects for request type:
# clean-up events (Müllsammelaktionen)
#

class CleanupEventRequestCreateView(RequestFormMixin, ObjectCreateView):
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
    # add to context: information about request workflow
    context['request_workflow'] = {
      'steps': 5,
      'current_step': 1,
    }
    return context


class CleanupEventRequestUpdateView(RequestFormMixin, ObjectUpdateView):
  """
  view for form page for updating an instance of object for request type clean-up events
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
    # add to context: information about request workflow
    context['request_workflow'] = {
      'steps': 5,
      'current_step': 1,
    }
    return context


class CleanupEventEventCreateView(RequestFollowUpFormMixin, ObjectCreateView):
  """
  view for form page for creating an instance of object for request type clean-up events
  (Müllsammelaktionen):
  event (Aktion)
  """

  model = CleanupEventEvent

  def get_form_kwargs(self):
    """
    returns ``**kwargs`` as a dictionary with form attributes

    :return: ``**kwargs`` as a dictionary with form attributes
    """
    kwargs = super().get_form_kwargs()
    # pass request field to form
    kwargs['request_field'] = 'cleanupevent_request'
    # get corresponding request object via ID passed in session
    # and pass it to form
    kwargs['request_object'] = get_request(
      CleanupEventRequest,
      self.request.session.get('request_id', None),
      only_primary_key=False
    )
    return kwargs

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add to context: information about request workflow
    context['request_workflow'] = {
      'steps': 5,
      'current_step': 2,
    }
    # add to context: URLs
    context['back_url'] = reverse(
      'antragsmanagement:cleanupeventrequest_update',
      args=[self.request.session.get('request_id', None)]
    )
    return context

  def get_initial(self):
    """
    conditionally sets initial field values for this view

    :return: dictionary with initial field values for this view
    """
    # get corresponding request object via ID passed in session
    # and set request to it
    return {
      'cleanupevent_request': get_request(
        CleanupEventRequest, self.request.session.get('request_id', None))
    }
