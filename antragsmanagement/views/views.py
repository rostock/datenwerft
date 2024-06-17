from django.conf import settings
from django.views.generic.base import TemplateView

from .base import ObjectCreateView, ObjectUpdateView
from .forms import RequestForm, RequestFollowUpForm
from .functions import add_permissions_context_elements, add_useragent_context_elements
from antragsmanagement.models import CodelistRequestStatus, Authority, Email, Requester, \
  CleanupEventRequest, CleanupEventEvent
from antragsmanagement.utils import get_corresponding_requester


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


class RequestCreateView(ObjectCreateView):
  """
  view for form page for creating an instance of general object:
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
    # add information about corresponding requester object for user to context
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


#
# objects for request type:
# clean-up events (Müllsammelaktionen)
#

class CleanupEventRequestCreateView(RequestCreateView):
  """
  view for form page for creating an instance of object for request type clean-up events
  (Müllsammelaktionen):
  request (Antrag)
  """

  model = CleanupEventRequest


class CleanupEventEventCreateView(ObjectCreateView):
  """
  view for form page for creating an instance of object for request type clean-up events
  (Müllsammelaktionen):
  request (Antrag)
  """

  template_name = 'antragsmanagement/form-request-followup.html'
  model = CleanupEventEvent
  form = RequestFollowUpForm

  def get_form_kwargs(self):
    """
    returns ``**kwargs`` as a dictionary with form attributes

    :return: ``**kwargs`` as a dictionary with form attributes
    """
    kwargs = super().get_form_kwargs()
    # pass request field to form
    kwargs['request_field'] = 'cleanupevent_request'
    # pass request object to form
    kwargs['request_object'] = CleanupEventRequest.objects.filter(
      id=self.request.session['request_id'])
    return kwargs

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
    # add information about corresponding request object to context
    context['corresponding_request'] = self.request.session['request_id']
    return context

  def get_initial(self):
    """
    conditionally sets initial field values for this view

    :return: dictionary with initial field values for this view
    """
    # set request to request passed in session
    cleanupevent_request_id = self.request.session['request_id']
    if CleanupEventRequest.objects.filter(id=cleanupevent_request_id).exists():
      cleanupevent_request = CleanupEventRequest.objects.get(id=cleanupevent_request_id)
    else:
      cleanupevent_request = None
    return {
      'cleanupevent_request': cleanupevent_request
    }
