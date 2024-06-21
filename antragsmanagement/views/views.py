from django.contrib.gis.db.models.functions import AsGeoJSON
from django.urls import reverse
from django.views.generic.base import TemplateView

from antragsmanagement.constants_vars import REQUESTERS, ADMINS
from antragsmanagement.models import GeometryObject, CodelistRequestStatus, Authority, Email, \
  Requester, CleanupEventRequest, CleanupEventEvent, CleanupEventVenue, CleanupEventDetails, \
  CleanupEventContainer
from antragsmanagement.utils import get_corresponding_requester, get_request
from toolbox.utils import is_geometry_field
from antragsmanagement.views.base import ObjectTableDataView, ObjectTableView, ObjectCreateView, \
  ObjectUpdateView
from antragsmanagement.views.forms import RequestForm, RequestFollowUpForm, \
  CleanupEventEventForm, CleanupEventDetailsForm, CleanupEventContainerForm
from antragsmanagement.views.functions import add_permissions_context_elements, \
  add_useragent_context_elements


#
# general
#

class IndexView(TemplateView):
  """
  view for main page

  :param template_name: template name
  """

  template_name = 'antragsmanagement/index.html'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # remove any ID in session
    self.request.session.pop('request_id', None)
    self.request.session.pop('cleanupeventevent_id', None)
    self.request.session.pop('cleanupeventvenue_id', None)
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

class AuthorityTableDataView(ObjectTableDataView):
  """
  view for composing table data out of instances of general object:
  authority (Behörde)

  :param model: model
  :param update_view_name: name of view for form page for updating
  """

  model = Authority
  update_view_name = 'antragsmanagement:authority_update'


class AuthorityTableView(ObjectTableView):
  """
  view for table page for instances of general object:
  authority (Behörde)

  :param model: model
  :param table_data_view_name: name of view for composing table data out of instances
  :param icon_name: icon name
  """

  model = Authority
  table_data_view_name = 'antragsmanagement:authority_tabledata'
  icon_name = 'authority'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add permissions related context elements:
    # set admin permissions as necessary permissions
    context = add_permissions_context_elements(context, self.request.user, ADMINS)
    return context


class AuthorityUpdateView(ObjectUpdateView):
  """
  view for form page for updating an instance of general object:
  authority (Behörde)

  :param model: model
  :param cancel_url: custom cancel URL
  """

  model = Authority
  cancel_url = 'antragsmanagement:authority_table'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add permissions related context elements:
    # set admin permissions as necessary permissions
    context = add_permissions_context_elements(context, self.request.user, ADMINS)
    return context


class EmailTableDataView(ObjectTableDataView):
  """
  view for composing table data out of instances of general object:
  email (E-Mail)

  :param model: model
  :param update_view_name: name of view for form page for updating
  """

  model = Email
  update_view_name = 'antragsmanagement:email_update'


class EmailTableView(ObjectTableView):
  """
  view for table page for instances of general object:
  email (E-Mail)

  :param model: model
  :param table_data_view_name: name of view for composing table data out of instances
  :param icon_name: icon name
  """

  model = Email
  table_data_view_name = 'antragsmanagement:email_tabledata'
  icon_name = 'email'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add permissions related context elements:
    # set admin permissions as necessary permissions
    context = add_permissions_context_elements(context, self.request.user, ADMINS)
    return context


class EmailUpdateView(ObjectUpdateView):
  """
  view for form page for updating an instance of general object:
  email (E-Mail)

  :param model: model
  :param cancel_url: custom cancel URL
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
    context = add_permissions_context_elements(context, self.request.user, ADMINS)
    return context


class RequesterCreateView(ObjectCreateView):
  """
  view for form page for creating an instance of general object:
  requester (Antragsteller:in)

  :param model: model
  :param success_message: custom success message
  """

  model = Requester
  success_message = '<strong>Kontaktdaten</strong> erfolgreich gespeichert!'

  def form_valid(self, form):
    """
    sends HTTP response if passed form is valid

    :param form: form
    :return: HTTP response if passed form is valid
    """
    if self.request.user.is_authenticated:
      instance = form.save(commit=False)
      # set the value of the user_id field programmatically
      instance.user_id = self.request.user.pk
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
    context = add_permissions_context_elements(context, self.request.user, REQUESTERS)
    return context


class RequesterUpdateView(ObjectUpdateView):
  """
  view for form page for updating an instance of general object:
  requester (Antragsteller:in)

  :param model: model
  :param success_message: custom success message
  """

  model = Requester
  success_message = '<strong>Kontaktdaten</strong> erfolgreich aktualisiert!'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add permissions related context elements:
    # set requester permissions as necessary permissions
    context = add_permissions_context_elements(context, self.request.user, REQUESTERS)
    return context


class RequestFormMixin:
  """
  mixin for form page for creating or updating an instance of general object:
  request (Antrag)

  :param template_name: template name
  :param form: form
  :param success_message: custom success message
  :param request_workflow: request workflow informations
  """

  template_name = 'antragsmanagement/form-request.html'
  form = RequestForm
  success_message = 'Antragsdaten erfolgreich gespeichert!'
  request_workflow = {
    'steps': 5,
    'current_step': 1
  }

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
    instance = form.save(commit=False)
    instance.full_clean()
    instance.save()
    # store ID of new request in session in order to pass it to next view
    self.request.session['request_id'] = instance.pk
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
    context = add_permissions_context_elements(context, self.request.user, REQUESTERS)
    # add to context: information about corresponding requester object for user
    context['corresponding_requester'] = get_corresponding_requester(self.request.user)
    # add to context: information about request workflow
    context['request_workflow'] = self.request_workflow
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

  :param template_name: template name
  :param form: form
  :param success_message: custom success message
  :param request_workflow: request workflow informations
  """

  template_name = 'antragsmanagement/form-request-followup.html'
  form = RequestFollowUpForm
  success_message = 'Antragsdaten erfolgreich gespeichert!'
  request_workflow = {}

  def form_invalid(self, form, **kwargs):
    """
    re-opens passed form if it is not valid
    (purpose: keep geometry)

    :param form: form
    :return: passed form if it is not valid
    """
    context_data = self.get_context_data(**kwargs)
    form.data = form.data.copy()
    for field in self.model._meta.get_fields():
      # keep geometry (otherwise it would be lost on re-rendering)
      if is_geometry_field(field.__class__):
        geometry = form.data.get(field.name, None)
        if geometry and '0,0' not in geometry and '[]' not in geometry:
          context_data['geometry'] = geometry
    context_data['form'] = form
    return self.render_to_response(context_data)

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add permissions related context elements:
    # set requester permissions as necessary permissions
    context = add_permissions_context_elements(context, self.request.user, REQUESTERS)
    # add to context: request ID passed in session
    context['corresponding_request'] = self.request.session.get('request_id', None)
    # add to context: information about request workflow
    context['request_workflow'] = self.request_workflow
    # add to context: GeoJSONified geometry
    if self.object and issubclass(self.model, GeometryObject):
      geometry = getattr(self.object, self.model.BaseMeta.geometry_field)
      if geometry:
        geometry = self.model.objects.annotate(
          geojson=AsGeoJSON(geometry)
        ).get(pk=self.object.pk).geojson
      context['geometry'] = geometry
    return context


#
# objects for request type:
# clean-up events (Müllsammelaktionen)
#

class CleanupEventRequestCreateView(RequestFormMixin, ObjectCreateView):
  """
  view for form page for creating an instance of object for request type clean-up events
  (Müllsammelaktionen):
  request (Antrag)

  :param model: model
  :param request_workflow: request workflow informations
  """

  model = CleanupEventRequest
  request_workflow = {
    'steps': 5,
    'current_step': 1
  }


class CleanupEventRequestUpdateView(RequestFormMixin, ObjectUpdateView):
  """
  view for form page for updating an instance of object for request type clean-up events
  (Müllsammelaktionen):
  request (Antrag)

  :param model: model
  :param request_workflow: request workflow informations
  """

  model = CleanupEventRequest
  success_message = 'Antragsdaten erfolgreich aktualisiert!'
  request_workflow = {
    'steps': 5,
    'current_step': 1
  }

  def get_success_url(self):
    """
    defines the URL called in case of successful request

    :return: URL called in case of successful request
    """
    if self.request.session.get('cleanupeventevent_id', None):
      return reverse(
        viewname='antragsmanagement:cleanupeventevent_update',
        kwargs={'pk': self.request.session['cleanupeventevent_id']}
      )
    else:
      return reverse('antragsmanagement:cleanupeventevent_create')


class CleanupEventEventCreateView(RequestFollowUpFormMixin, ObjectCreateView):
  """
  view for form page for creating an instance of object for request type clean-up events
  (Müllsammelaktionen):
  event (Aktion)

  :param model: model
  :param form: form
  :param request_workflow: request workflow informations
  """

  model = CleanupEventEvent
  form = CleanupEventEventForm
  request_workflow = {
    'steps': 5,
    'current_step': 2
  }

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
    if self.request.session.get('request_id', None):
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
    # add to context: URLs
    context['back_url'] = reverse(
      viewname='antragsmanagement:cleanupeventrequest_update',
      kwargs={'pk': self.request.session.get('request_id', None)}
    )
    return context

  def get_initial(self):
    """
    conditionally sets initial field values for this view

    :return: dictionary with initial field values for this view
    """
    # get corresponding request object via ID passed in session
    # and set request to it
    if self.request.session.get('request_id', None):
      return {
        'cleanupevent_request': get_request(
          CleanupEventRequest, self.request.session.get('request_id', None))
      }
    return {}

  def form_valid(self, form):
    """
    sends HTTP response if passed form is valid

    :param form: form
    :return: HTTP response if passed form is valid
    """
    # delay necessary to allow automatic field contents to populate
    instance = form.save(commit=False)
    instance.full_clean()
    instance.save()
    # store ID of current object in session in order to pass it to previous view
    self.request.session['cleanupeventevent_id'] = instance.pk
    return super().form_valid(form)


class CleanupEventEventUpdateView(RequestFollowUpFormMixin, ObjectUpdateView):
  """
  view for form page for updating an instance of object for request type clean-up events
  (Müllsammelaktionen):
  event (Aktion)

  :param model: model
  :param form: form
  :param request_workflow: request workflow informations
  """

  model = CleanupEventEvent
  success_message = 'Antragsdaten erfolgreich aktualisiert!'
  form = CleanupEventEventForm
  request_workflow = {
    'steps': 5,
    'current_step': 2
  }

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add to context: URLs
    context['back_url'] = reverse(
      viewname='antragsmanagement:cleanupeventrequest_update',
      kwargs={'pk': self.request.session.get('request_id', None)}
    )
    return context

  def get_initial(self):
    """
    conditionally sets initial field values for this view

    :return: dictionary with initial field values for this view
    """
    initial_field_values = {}
    for field in self.model._meta.get_fields():
      if field.__class__.__name__ == 'DateField':
        value = getattr(self.model.objects.get(pk=self.object.pk), field.name)
        initial_field_values[field.name] = value.strftime('%Y-%m-%d') if value else None
    return initial_field_values

  def get_success_url(self):
    """
    defines the URL called in case of successful request

    :return: URL called in case of successful request
    """
    if self.request.session.get('cleanupeventvenue_id', None):
      return reverse(
        viewname='antragsmanagement:cleanupeventvenue_update',
        kwargs={'pk': self.request.session['cleanupeventvenue_id']}
      )
    else:
      return reverse('antragsmanagement:cleanupeventvenue_create')

  def form_valid(self, form):
    """
    sends HTTP response if passed form is valid

    :param form: form
    :return: HTTP response if passed form is valid
    """
    # delay necessary to allow automatic field contents to populate
    instance = form.save(commit=False)
    instance.full_clean()
    instance.save()
    # store ID of current object in session in order to pass it to previous view
    self.request.session['cleanupeventevent_id'] = instance.pk
    return super().form_valid(form)


class CleanupEventVenueCreateView(RequestFollowUpFormMixin, ObjectCreateView):
  """
  view for form page for creating an instance of object for request type clean-up events
  (Müllsammelaktionen):
  venue (Treffpunkt)

  :param model: model
  :param request_workflow: request workflow informations
  """

  model = CleanupEventVenue
  request_workflow = {
    'steps': 5,
    'current_step': 3
  }

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
    if self.request.session.get('request_id', None):
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
    # add to context: URLs
    context['back_url'] = reverse(
      viewname='antragsmanagement:cleanupeventevent_update',
      kwargs={'pk': self.request.session.get('cleanupeventevent_id', None)}
    )
    return context

  def get_initial(self):
    """
    conditionally sets initial field values for this view

    :return: dictionary with initial field values for this view
    """
    # get corresponding request object via ID passed in session
    # and set request to it
    if self.request.session.get('request_id', None):
      return {
        'cleanupevent_request': get_request(
          CleanupEventRequest, self.request.session.get('request_id', None))
      }
    return {}

  def form_valid(self, form):
    """
    sends HTTP response if passed form is valid

    :param form: form
    :return: HTTP response if passed form is valid
    """
    # delay necessary to allow automatic field contents to populate
    instance = form.save(commit=False)
    instance.full_clean()
    instance.save()
    # store ID of current object in session in order to pass it to previous view
    self.request.session['cleanupeventvenue_id'] = instance.pk
    return super().form_valid(form)


class CleanupEventVenueUpdateView(RequestFollowUpFormMixin, ObjectUpdateView):
  """
  view for form page for updating an instance of object for request type clean-up events
  (Müllsammelaktionen):
  venue (Treffpunkt)

  :param model: model
  :param request_workflow: request workflow informations
  """

  model = CleanupEventVenue
  success_message = 'Antragsdaten erfolgreich aktualisiert!'
  request_workflow = {
    'steps': 5,
    'current_step': 3
  }

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add to context: URLs
    context['back_url'] = reverse(
      viewname='antragsmanagement:cleanupeventevent_update',
      kwargs={'pk': self.request.session.get('cleanupeventevent_id', None)}
    )
    return context

  def get_success_url(self):
    """
    defines the URL called in case of successful request

    :return: URL called in case of successful request
    """
    if self.request.session.get('cleanupeventdetails_id', None):
      return reverse(
        viewname='antragsmanagement:cleanupeventdetails_update',
        kwargs={'pk': self.request.session['cleanupeventdetails_id']}
      )
    else:
      return reverse('antragsmanagement:cleanupeventdetails_create')

  def form_valid(self, form):
    """
    sends HTTP response if passed form is valid

    :param form: form
    :return: HTTP response if passed form is valid
    """
    # delay necessary to allow automatic field contents to populate
    instance = form.save(commit=False)
    instance.full_clean()
    instance.save()
    # store ID of current object in session in order to pass it to previous view
    self.request.session['cleanupeventvenue_id'] = instance.pk
    return super().form_valid(form)


class CleanupEventDetailsCreateView(RequestFollowUpFormMixin, ObjectCreateView):
  """
  view for form page for creating an instance of object for request type clean-up events
  (Müllsammelaktionen):
  details (Detailangaben)

  :param model: model
  :param form: form
  :param request_workflow: request workflow informations
  """

  model = CleanupEventDetails
  form = CleanupEventDetailsForm
  request_workflow = {
    'steps': 5,
    'current_step': 4
  }

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
    if self.request.session.get('request_id', None):
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
    # add to context: URLs
    context['back_url'] = reverse(
      viewname='antragsmanagement:cleanupeventvenue_update',
      kwargs={'pk': self.request.session.get('cleanupeventvenue_id', None)}
    )
    return context

  def get_initial(self):
    """
    conditionally sets initial field values for this view

    :return: dictionary with initial field values for this view
    """
    # get corresponding request object via ID passed in session
    # and set request to it
    if self.request.session.get('request_id', None):
      return {
        'cleanupevent_request': get_request(
          CleanupEventRequest, self.request.session.get('request_id', None))
      }
    return {}

  def form_valid(self, form):
    """
    sends HTTP response if passed form is valid

    :param form: form
    :return: HTTP response if passed form is valid
    """
    # delay necessary to allow automatic field contents to populate
    instance = form.save(commit=False)
    instance.full_clean()
    instance.save()
    # store ID of current object in session in order to pass it to previous view
    self.request.session['cleanupeventdetails_id'] = instance.pk
    return super().form_valid(form)


class CleanupEventDetailsUpdateView(RequestFollowUpFormMixin, ObjectUpdateView):
  """
  view for form page for updating an instance of object for request type clean-up events
  (Müllsammelaktionen):
  details (Detailangaben)

  :param model: model
  :param form: form
  :param request_workflow: request workflow informations
  """

  model = CleanupEventDetails
  success_message = 'Antragsdaten erfolgreich aktualisiert!'
  form = CleanupEventDetailsForm
  request_workflow = {
    'steps': 5,
    'current_step': 4
  }

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add to context: URLs
    context['back_url'] = reverse(
      viewname='antragsmanagement:cleanupeventvenue_update',
      kwargs={'pk': self.request.session.get('cleanupeventvenue_id', None)}
    )
    return context

  def get_success_url(self):
    """
    defines the URL called in case of successful request

    :return: URL called in case of successful request
    """
    return reverse('antragsmanagement:cleanupeventcontainer_create')

  def form_valid(self, form):
    """
    sends HTTP response if passed form is valid

    :param form: form
    :return: HTTP response if passed form is valid
    """
    # delay necessary to allow automatic field contents to populate
    instance = form.save(commit=False)
    instance.full_clean()
    instance.save()
    # store ID of current object in session in order to pass it to previous view
    self.request.session['cleanupeventdetails_id'] = instance.pk
    return super().form_valid(form)


class CleanupEventContainerCreateView(RequestFollowUpFormMixin, ObjectCreateView):
  """
  view for form page for creating an instance of object for request type clean-up events
  (Müllsammelaktionen):
  container (Container)

  :param model: model
  :param form: form
  :param request_workflow: request workflow informations
  """

  model = CleanupEventContainer
  form = CleanupEventContainerForm
  request_workflow = {
    'steps': 5,
    'current_step': 5
  }
  success_message = '<strong>Antrag auf Müllsammelaktion</strong> erfolgreich gespeichert!'

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
    if self.request.session.get('request_id', None):
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
    # add to context: URLs
    context['back_url'] = reverse(
      viewname='antragsmanagement:cleanupeventdetails_update',
      kwargs={'pk': self.request.session.get('cleanupeventdetails_id', None)}
    )
    return context

  def get_initial(self):
    """
    conditionally sets initial field values for this view

    :return: dictionary with initial field values for this view
    """
    # get corresponding request object via ID passed in session
    # and set request to it
    if self.request.session.get('request_id', None):
      return {
        'cleanupevent_request': get_request(
          CleanupEventRequest, self.request.session.get('request_id', None))
      }
    return {}
