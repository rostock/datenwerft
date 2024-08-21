from datetime import date, datetime
from django.conf import settings
from django.contrib import messages
from django.contrib.gis.geos import GEOSGeometry
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic.base import TemplateView
from django_ratelimit.decorators import ratelimit
from jsonview.views import JsonView

from .base import ObjectTableDataView, ObjectTableView, ObjectCreateView, \
  ObjectUpdateView, ObjectDeleteView
from .forms import ObjectForm, RequesterForm, RequestForm, RequestFollowUpForm, \
  CleanupEventEventForm, CleanupEventDetailsForm, CleanupEventContainerForm
from .functions import add_model_context_elements, add_permissions_context_elements, \
  add_useragent_context_elements, additional_messages, clean_initial_field_values, \
  get_cleanupeventrequest_anonymous_api_feature, get_cleanupeventrequest_anonymous_feature, \
  get_cleanupeventrequest_feature, get_cleanupeventrequest_queryset, \
  get_corresponding_cleanupeventrequest_geometry, get_referer, get_referer_url, geometry_keeper, \
  send_cleanupeventrequest_email
from antragsmanagement.constants_vars import REQUESTERS, AUTHORITIES, ADMINS
from antragsmanagement.models import GeometryObject, CodelistRequestStatus, Authority, Email, \
  Requester, CleanupEventRequest, CleanupEventEvent, CleanupEventVenue, CleanupEventDetails, \
  CleanupEventContainer, CleanupEventDump
from antragsmanagement.utils import check_necessary_permissions, \
  belongs_to_antragsmanagement_authority, get_corresponding_requester, get_icon_from_settings, \
  get_request
from toolbox.utils import format_date_datetime


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
    self.request.session.pop('cleanupeventdetails_id', None)
    # add user agent related context elements
    context = add_useragent_context_elements(context, self.request)
    # add permissions related context elements
    context = add_permissions_context_elements(context, self.request.user)
    # add to context: information about corresponding requester object for user or request
    if self.request.user.is_authenticated:
      context['corresponding_requester'] = get_corresponding_requester(self.request.user)
    else:
      context['corresponding_requester'] = get_corresponding_requester(
        user=None, request=self.request)
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
  :param permissions_level: permissions level user has to have
  """

  model = Authority
  update_view_name = 'antragsmanagement:authority_update'
  permissions_level = 'ADMINS'


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
  :param permissions_level: permissions level user has to have
  """

  model = Email
  update_view_name = 'antragsmanagement:email_update'
  permissions_level = 'ADMINS'


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
  cancel_url = 'antragsmanagement:email_table'

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


class RequesterMixin:
  """
  mixin for form page for creating an instance of general object:
  requester (Antragsteller:in)

  :param model: model
  :param form: form
  :param success_message: custom success message
  """

  model = Requester
  form = RequesterForm
  success_message = '<strong>Kontaktdaten</strong> erfolgreich gespeichert!'

  def form_valid(self, form):
    """
    sends HTTP response if passed form is valid

    :param form: form
    :return: HTTP response if passed form is valid
    """
    # store ID of requester in session in order to pass it to next view
    # if user is not authenticated
    if not self.request.user.is_authenticated:
      instance = form.save(commit=True)
      self.request.session['corresponding_requester'] = instance.pk
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


class RequesterCreateView(RequesterMixin, ObjectCreateView):
  """
  view for form page for creating an instance of general object:
  requester (Antragsteller:in)
  """

  def form_valid(self, form):
    """
    sends HTTP response if passed form is valid

    :param form: form
    :return: HTTP response if passed form is valid
    """
    # set value of user_id field
    # if user is authenticated
    if self.request.user.is_authenticated:
      instance = form.save(commit=False)
      instance.user_id = self.request.user.pk
    return super().form_valid(form)


class RequesterUpdateView(RequesterMixin, ObjectUpdateView):
  """
  view for form page for updating an instance of general object:
  requester (Antragsteller:in)

  :param success_message: custom success message
  """

  success_message = '<strong>Kontaktdaten</strong> erfolgreich aktualisiert!'


class RequestMixin:
  """
  mixin for form page for creating or updating an instance of general object:
  request (Antrag)

  :param template_name: template name
  :param form: form
  :param success_message: custom success message
  """

  template_name = 'antragsmanagement/form_request.html'
  form = RequestForm
  success_message = 'Antragsdaten erfolgreich gespeichert!'

  def get_form_kwargs(self):
    """
    returns ``**kwargs`` as a dictionary with form attributes

    :return: ``**kwargs`` as a dictionary with form attributes
    """
    kwargs = super().get_form_kwargs()
    # pass requester to form
    if self.request.user.is_authenticated:
      kwargs['requester'] = get_corresponding_requester(
        user=self.request.user, request=None, only_primary_key=False)
    else:
      kwargs['requester'] = get_corresponding_requester(
        user=None, request=self.request, only_primary_key=False)
    return kwargs

  def post(self, request, *args, **kwargs):
    if 'cancel' in request.POST:
      if self.get_object():
        self.get_object().delete()
        messages.warning(request, self.cancel_message)
      if request.user.is_authenticated:
        return redirect('antragsmanagement:index')
      else:
        return redirect('antragsmanagement:anonymous_index')
    return super().post(request, *args, **kwargs)

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
    # remove any custom success message in session
    # add permissions related context elements:
    # set requester permissions as necessary permissions
    context = add_permissions_context_elements(context, self.request.user, REQUESTERS)
    # add to context: information about corresponding requester object for user or request
    if self.request.user.is_authenticated:
      context['corresponding_requester'] = get_corresponding_requester(self.request.user)
    else:
      context['corresponding_requester'] = get_corresponding_requester(
        user=None, request=self.request)
    # add to context: information about request workflow
    context['request_workflow'] = self.request_workflow
    # add to context: disabled fields
    context['disabled_fields'] = ['status', 'requester']
    return context

  def get_initial(self):
    """
    conditionally sets initial field values for this view

    :return: dictionary with initial field values for this view
    """
    # set status to default status
    # and set requester to corresponding requester object for user or request
    if self.request.user.is_authenticated:
      requester = get_corresponding_requester(self.request.user)
    else:
      requester = get_corresponding_requester(user=None, request=self.request)
    return {
      'status': CodelistRequestStatus.get_status_new(),
      'requester': requester if requester else Requester.objects.none()
    }


class RequestFollowUpMixin:
  """
  mixin for form page for creating or updating a follow-up instance of general object:
  request (Antrag)

  :param template_name: template name
  :param form: form
  :param success_message: custom success message
  """

  template_name = 'antragsmanagement/form_request-followup.html'
  form = RequestFollowUpForm
  success_message = 'Antragsdaten erfolgreich gespeichert!'

  def get_form_kwargs(self):
    """
    returns ``**kwargs`` as a dictionary with form attributes

    :return: ``**kwargs`` as a dictionary with form attributes
    """
    kwargs = super().get_form_kwargs()
    # pass request field to form
    kwargs['request_field'] = self.request_field
    # get corresponding request object via ID passed in session
    # and pass it to form
    if self.request.session.get('request_id', None):
      kwargs['request_object'] = get_request(
        self.request_model,
        self.request.session.get('request_id', None),
        only_primary_key=False
      )
    return kwargs

  def post(self, request, *args, **kwargs):
    if 'cancel' in request.POST:
      if self.request.session.get('request_id', None):
        try:
          request_object = get_request(
            self.request_model,
            self.request.session.get('request_id', None),
            only_primary_key=False
          )
          request_object.delete()
          messages.warning(request, self.cancel_message)
        except self.request_model.DoesNotExist:
            raise Http404(self.error_message)
      if request.user.is_authenticated:
        return redirect('antragsmanagement:index')
      else:
        return redirect('antragsmanagement:anonymous_index')
    return super().post(request, *args, **kwargs)

  def form_invalid(self, form, **kwargs):
    """
    re-opens passed form if it is not valid
    (purpose: keep geometry)

    :param form: form
    :return: passed form if it is not valid
    """
    context_data = self.get_context_data(form=form)
    form.data = form.data.copy()
    context_data = geometry_keeper(form.data, self.model, context_data)
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
    # add to context: disabled fields
    context['disabled_fields'] = [self.request_field]
    if issubclass(self.model, GeometryObject):
      if self.object:
        # add to context: GeoJSONified geometry
        geometry = getattr(self.object, self.model.BaseMeta.geometry_field)
        if geometry:
          context['geometry'] = GEOSGeometry(geometry).geojson
    return context


class RequestFollowUpAuthorativeMixin:
  """
  mixin for authorative form page in terms of a follow-up instance of general object:
  request (Antrag)

  :param success_message: custom success message
  :param request_workflow: request workflow informations
  """

  # override success message
  success_message = ObjectUpdateView.success_message.replace('<strong>', 'zu <strong>')
  # empty workflow
  request_workflow = {}

  def form_invalid(self, form, **kwargs):
    """
    re-opens passed form if it is not valid
    (purpose: keep original referer)

    :param form: form
    :return: passed form if it is not valid
    """
    context_data = self.get_context_data(form=form)
    form.data = form.data.copy()
    context_data['cancel_url'] = form.data.get('original_referer', None)
    return self.render_to_response(context_data)

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add to context: authorative hint
    context['authorative'] = True
    # add to context: hidden and disabled fields
    context['hidden_fields'] = ['cleanupevent_request']
    context['disabled_fields'] = []
    # add to context: URLs
    context['cancel_url'] = get_referer_url(
      referer=get_referer(self.request),
      fallback='antragsmanagement:index'
    )
    # add permissions related context elements:
    # set authority permissions as necessary permissions
    context = add_permissions_context_elements(context, self.request.user, AUTHORITIES)
    return context

  def get_initial(self):
    """
    conditionally sets initial field values for this view

    :return: dictionary with initial field values for this view
    """
    return clean_initial_field_values(
      fields=self.model._meta.get_fields(),
      model=self.model,
      curr_obj=self.object
    )

  def get_success_url(self):
    """
    defines the URL called in case of successful request

    :return: URL called in case of successful request
    """
    referer = self.request.POST.get('original_referer', '')
    if 'table' in referer:
      return reverse('antragsmanagement:cleanupeventrequest_table')
    elif 'map' in referer:
      return reverse('antragsmanagement:cleanupeventrequest_map')
    return reverse('antragsmanagement:index')


class RequestFollowUpDecisionMixin:
  """
  mixin for workflow decision page in terms of a follow-up instance of general object:
  request (Antrag)

  :param template_name: template name
  """

  template_name = 'antragsmanagement/decision.html'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add user agent related context elements
    context = add_useragent_context_elements(context, self.request)
    # add model related context elements
    context = add_model_context_elements(context, self.model)
    # add permissions related context elements:
    # set requester permissions as necessary permissions
    context = add_permissions_context_elements(context, self.request.user, REQUESTERS)
    # add to context: request ID passed in session
    context['corresponding_request'] = self.request.session.get('request_id', None)
    # add to context: information about request workflow
    context['request_workflow'] = self.request_workflow
    # add to context: text describing the decision
    context['decision_text'] = self.decision_text
    return context


class RequestFollowUpDeleteMixin:
  """
  mixin for form page for deleting a follow-up instance of general object:
  request (Antrag)

  :param success_message: custom success message
  """

  # override success message
  success_message = ObjectDeleteView.success_message.replace('<strong>', 'zu <strong>')

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add to context: URLs
    context['cancel_url'] = get_referer_url(
      referer=get_referer(self.request),
      fallback='antragsmanagement:index'
    )
    # add permissions related context elements:
    # set authority permissions as necessary permissions
    context = add_permissions_context_elements(context, self.request.user, AUTHORITIES)
    return context

  def get_success_url(self):
    """
    defines the URL called in case of successful request

    :return: URL called in case of successful request
    """
    referer = self.request.POST.get('original_referer', '')
    if 'table' in referer:
      return reverse('antragsmanagement:cleanupeventrequest_table')
    elif 'map' in referer:
      return reverse('antragsmanagement:cleanupeventrequest_map')
    return reverse('antragsmanagement:index')


#
# objects for request type:
# clean-up events (Müllsammelaktionen)
#

class CleanupEventRequestTableDataView(ObjectTableDataView):
  """
  view for composing table data out of instances of object
  for request type clean-up events (Müllsammelaktionen):
  request (Antrag)

  :param update_view_name: name of view for authorative form page for updating
  :param columns: table columns with names (as keys) and titles/headers (as values)
  """

  update_view_name = 'antragsmanagement:cleanupeventrequest_authorative_update'
  columns = {
    'id': 'ID',
    'created': 'Eingang',
    'status': 'Status',
    'requester': 'Antragsteller:in',
    'responsibilities': 'Zuständigkeit(en)',
    'event_from': 'von',
    'event_to': 'bis',
    'details_waste_quantity': 'Abfallmenge',
    'details_waste_types': 'Abfallart(en)',
    'details_equipments': 'Austattung(en)',
    'container_delivery': 'Container-Stellung',
    'container_pickup': 'Container-Abholung'
  }

  def get_initial_queryset(self):
    """
    loads initial queryset
    """
    if check_necessary_permissions(self.request.user, self.permissions_level):
      return get_cleanupeventrequest_queryset(self.request.user, False)
    return CleanupEventRequest.objects.none()

  def count_records(self, qs):
    """
    calculates the number of records in the queryset
    """
    return len(qs) if isinstance(qs, list) else qs.count()

  def prepare_results(self, qs):
    """
    loops passed queryset, creates cleaned-up JSON representation of the queryset and returns it

    :param qs: queryset
    :return: cleaned-up JSON representation of the queryset
    """
    json_data = []
    if check_necessary_permissions(self.request.user, self.permissions_level):
      for item in qs:
        item_data = []
        for column in item.keys():
          data, value = '', item[column]
          if value:
            # format dates and datetimes
            if isinstance(value, date) or isinstance(value, datetime):
              data = format_date_datetime(value)
            else:
              data = value
          item_data.append(data)
        # append links for authorative updating
        if (
            belongs_to_antragsmanagement_authority(self.request.user)
            or self.request.user.is_superuser
        ):
          if (
              self.request.user.has_perm('antragsmanagement.view_cleanupeventrequest')
              or self.request.user.has_perm('antragsmanagement.change_cleanupeventrequest')
          ):
            links = '<a class="mb-1 btn btn-sm btn-outline-warning" role="button" '
            links += 'title="Antrag ansehen oder bearbeiten" '
            links += 'href="' + reverse(
              viewname='antragsmanagement:cleanupeventrequest_authorative_update',
              kwargs={'pk': item['id']}
            ) + '">'
            links += '<i class="fas fa-' + get_icon_from_settings('update') + '"></i> '
            links += 'Antrag</a>'
            event = CleanupEventEvent.objects.filter(cleanupevent_request=item['id']).first()
            if event:
              links += '<a class="ms-1 mb-1 btn btn-sm btn-outline-warning" role="button" '
              links += 'title="Aktionsdaten ansehen oder bearbeiten" '
              links += 'href="' + reverse(
                viewname='antragsmanagement:cleanupeventevent_authorative_update',
                kwargs={'pk': event.pk}
              ) + '">'
              links += '<i class="fas fa-' + get_icon_from_settings('update') + '"></i> '
              links += 'Aktionsdaten</a>'
            venue = CleanupEventVenue.objects.filter(cleanupevent_request=item['id']).first()
            if venue:
              links += '<a class="ms-1 mb-1 btn btn-sm btn-outline-warning" role="button" '
              links += 'title="Treffpunkt ansehen oder bearbeiten" '
              links += 'href="' + reverse(
                viewname='antragsmanagement:cleanupeventvenue_authorative_update',
                kwargs={'pk': venue.pk}
              ) + '">'
              links += '<i class="fas fa-' + get_icon_from_settings('update') + '"></i> '
              links += 'Treffpunkt</a>'
            details = CleanupEventDetails.objects.filter(cleanupevent_request=item['id']).first()
            if details:
              links += '<a class="ms-1 mb-1 btn btn-sm btn-outline-warning" role="button" '
              links += 'title="Detailangaben ansehen oder bearbeiten" '
              links += 'href="' + reverse(
                viewname='antragsmanagement:cleanupeventdetails_authorative_update',
                kwargs={'pk': details.pk}
              ) + '">'
              links += '<i class="fas fa-' + get_icon_from_settings('update') + '"></i> '
              links += 'Detailangaben</a>'
            container = CleanupEventContainer.objects.filter(
              cleanupevent_request=item['id']).first()
            if container:
              links += '<a class="ms-1 mb-1 btn btn-sm btn-outline-warning" role="button" '
              links += 'title="Containerdaten ansehen oder bearbeiten" '
              links += 'href="' + reverse(
                viewname='antragsmanagement:cleanupeventcontainer_authorative_update',
                kwargs={'pk': container.pk}
              ) + '">'
              links += '<i class="fas fa-' + get_icon_from_settings('update') + '"></i> '
              links += 'Containerdaten</a>'
              links += '<a class="ms-1 mb-1 btn btn-sm btn-outline-danger" role="button" '
              links += 'title="Containerdaten löschen" '
              links += 'href="' + reverse(
                viewname='antragsmanagement:cleanupeventcontainer_delete',
                kwargs={'pk': container.pk}
              ) + '">'
              links += '<i class="fas fa-' + get_icon_from_settings('delete') + '"></i> '
              links += 'Containerdaten</a>'
            else:
              links += '<a class="ms-1 mb-1 btn btn-sm btn-outline-primary" role="button" '
              links += 'title="neue Containerdaten anlegen" '
              links += 'href="' + reverse(
                viewname='antragsmanagement:cleanupeventcontainer_authorative_create',
                kwargs={'request_id': item['id']}
              ) + '">'
              links += '<i class="fas fa-' + get_icon_from_settings('create') + '"></i> '
              links += 'Containerdaten</a>'
            dump = CleanupEventDump.objects.filter(cleanupevent_request=item['id']).first()
            if dump:
              links += '<a class="ms-1 mb-1 btn btn-sm btn-outline-warning" role="button" '
              links += 'title="Müllablageplatz ansehen oder bearbeiten" '
              links += 'href="' + reverse(
                viewname='antragsmanagement:cleanupeventdump_authorative_update',
                kwargs={'pk': dump.pk}
              ) + '">'
              links += '<i class="fas fa-' + get_icon_from_settings('update') + '"></i> '
              links += 'Müllablageplatz</a>'
              links += '<a class="ms-1 mb-1 btn btn-sm btn-outline-danger" role="button" '
              links += 'title="Müllablageplatz löschen" '
              links += 'href="' + reverse(
                viewname='antragsmanagement:cleanupeventdump_delete',
                kwargs={'pk': dump.pk}
              ) + '">'
              links += '<i class="fas fa-' + get_icon_from_settings('delete') + '"></i> '
              links += 'Müllablageplatz</a>'
            else:
              links += '<a class="ms-1 mb-1 btn btn-sm btn-outline-primary" role="button" '
              links += 'title="neuen Müllablageplatz anlegen" '
              links += 'href="' + reverse(
                viewname='antragsmanagement:cleanupeventdump_authorative_create',
                kwargs={'request_id': item['id']}
              ) + '">'
              links += '<i class="fas fa-' + get_icon_from_settings('create') + '"></i> '
              links += 'Müllablageplatz</a>'
            item_data.append(links)
        json_data.append(item_data)
    return json_data

  def filter_queryset(self, qs):
    """
    filters passed queryset

    :param qs: queryset
    :return: filtered queryset
    """
    def search(search_base, search_str):
      search_str_lower = search_str.lower()
      return [
        search_item for search_item in search_base
        if any(
          search_str_lower in format_date_datetime(value)
          if isinstance(value, (date, datetime))
          else search_str_lower in str(value).lower()
          for value in search_item.values()
        )
      ]
    current_search_str = self.request.GET.get('search[value]', None)
    if current_search_str:
      return search(qs, current_search_str)
    return qs

  def ordering(self, qs):
    """
    sorts passed queryset

    :param qs: queryset
    :return: sorted queryset
    """
    def sort_key(x):
      """
      returns a tuple where the first element is a boolean
      (True if value at the passed key in the passed dict is None, False otherwise)
      and the second element is the value at the passed key in the passed dict itself
      """
      return x[column_name] is None, x[column_name]
    # assume initial order since multiple column sorting is prohibited
    if self.request.GET.get('order[0][column]', None):
      order_column = self.request.GET.get('order[0][column]')
      order_dir = self.request.GET.get('order[0][dir]', None)
      column_name = list(self.columns.keys())[int(order_column)]
      reverse_order = True if order_dir is not None and order_dir == 'desc' else False
      return sorted(qs, key=sort_key, reverse=reverse_order)
    else:
      return qs


class CleanupEventRequestTableView(TemplateView):
  """
  view for table page for instances of object
  for request type clean-up events (Müllsammelaktionen):
  request (Antrag)

  :param model: model
  :param template_name: template name
  :param initial_order: initial order
  (careful here: adopt to CleanupEventRequestTableDataView.columns)
  :param table_data_view_name: name of view for composing table data out of instances
  :param icon_name: icon name
  """

  model = CleanupEventRequest
  template_name = 'antragsmanagement/table_request.html'
  initial_order = [0, 'desc']
  table_data_view_name = 'antragsmanagement:cleanupeventrequest_tabledata'
  icon_name = 'cleanupeventrequest'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add user agent related context elements
    context = add_useragent_context_elements(context, self.request)
    # add model related context elements
    context = add_model_context_elements(context, self.model)
    # add table related context elements
    context['objects_count'] = get_cleanupeventrequest_queryset(self.request.user, True)
    context['column_titles'] = list(CleanupEventRequestTableDataView.columns.values())
    context['initial_order'] = self.initial_order
    context['tabledata_url'] = reverse(self.table_data_view_name)
    # add to context: icon
    context['icon'] = self.icon_name
    # add permissions related context elements:
    context = add_permissions_context_elements(context, self.request.user)
    return context


class CleanupEventRequestMapDataView(JsonView):
  """
  view for composing map data out of instances of object
  for request type clean-up events (Müllsammelaktionen):
  request (Antrag)

  :param update_view_name: name of view for authorative form page for updating
  :param permissions_level: permissions level user has to have
  """

  update_view_name = 'antragsmanagement:cleanupeventrequest_authorative_update'
  permissions_level = ''

  def get_context_data(self, **kwargs):
    """
    returns GeoJSON feature collection

    :param kwargs:
    :return: GeoJSON feature collection
    """
    if check_necessary_permissions(self.request.user, self.permissions_level):
      objects = get_cleanupeventrequest_queryset(self.request.user, False)
      # declare empty GeoJSON feature collection
      feature_collection = {
        'type': 'FeatureCollection',
        'features': []
      }
      # handle objects
      if objects:
        authorative_rights = False
        if (
            belongs_to_antragsmanagement_authority(self.request.user)
            or self.request.user.is_superuser
        ):
          if (
              self.request.user.has_perm('antragsmanagement.view_cleanupeventrequest')
              or self.request.user.has_perm('antragsmanagement.change_cleanupeventrequest')
          ):
            authorative_rights = True
        for curr_object in objects:
          # add GeoJSON feature for event to GeoJSON feature collection
          event = get_cleanupeventrequest_feature(
            curr_object=curr_object,
            curr_type='event',
            authorative_rights=authorative_rights
          )
          if event:
            feature_collection['features'].append(event)
          # add GeoJSON feature for venue to GeoJSON feature collection
          venue = get_cleanupeventrequest_feature(
            curr_object=curr_object,
            curr_type='venue',
            authorative_rights=authorative_rights
          )
          if venue:
            feature_collection['features'].append(venue)
          # add GeoJSON feature for container to GeoJSON feature collection
          container = get_cleanupeventrequest_feature(
            curr_object=curr_object,
            curr_type='container',
            authorative_rights=authorative_rights
          )
          if container:
            feature_collection['features'].append(container)
          # add GeoJSON feature for dump to GeoJSON feature collection
          dump = get_cleanupeventrequest_feature(
            curr_object=curr_object,
            curr_type='dump',
            authorative_rights=authorative_rights
          )
          if dump:
            feature_collection['features'].append(dump)
      return feature_collection
    return HttpResponse(
      content='{"has_necessary_permissions": false}', content_type="application/json"
    )


class CleanupEventRequestMapView(TemplateView):
  """
  view for map page for instances of object
  for request type clean-up events (Müllsammelaktionen):
  request (Antrag)

  :param model: model
  :param template_name: template name
  :param map_data_view_name: name of view for composing map data out of instances
  :param icon_name: icon name
  """

  model = CleanupEventRequest
  template_name = 'antragsmanagement/map_request.html'
  map_data_view_name = 'antragsmanagement:cleanupeventrequest_mapdata'
  icon_name = 'cleanupeventrequest'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add user agent related context elements
    context = add_useragent_context_elements(context, self.request)
    # add model related context elements
    context = add_model_context_elements(context, self.model)
    # add map related context elements
    context['LEAFLET_CONFIG'] = settings.LEAFLET_CONFIG
    context['objects_count'] = get_cleanupeventrequest_queryset(self.request.user, True)
    context['mapdata_url'] = reverse(self.map_data_view_name)
    # add filter related information to context
    context['requests_status'] = list(
      CleanupEventRequest.objects.values_list(
        'status__name', flat=True).distinct().order_by('status')
    )
    # add to context: icon
    context['icon'] = self.icon_name
    # add permissions related context elements:
    context = add_permissions_context_elements(context, self.request.user)
    return context


class CleanupEventRequestCreateView(RequestMixin, ObjectCreateView):
  """
  view for workflow page for creating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  request (Antrag)

  :param model: model
  :param request_workflow: request workflow informations
  """

  model = CleanupEventRequest
  request_workflow = {
    'steps': 5,
    'current_step': 1
  }

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add to context: hidden fields
    context['hidden_fields'] = ['comment']
    return context


class CleanupEventRequestUpdateView(RequestMixin, ObjectUpdateView):
  """
  view for workflow page for updating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  request (Antrag)

  :param model: model
  :param cancel_message: custom cancel message
  :param success_message: custom success message
  :param request_workflow: request workflow informations
  """

  model = CleanupEventRequest
  cancel_message = '<strong>Antrag auf Müllsammelaktion</strong> abgebrochen'
  success_message = 'Antragsdaten erfolgreich aktualisiert!'
  request_workflow = {
    'steps': 5,
    'current_step': 1
  }

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add to context: hidden fields
    context['hidden_fields'] = ['comment']
    return context

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


class CleanupEventRequestAuthorativeUpdateView(RequestMixin, ObjectUpdateView):
  """
  view for authorative form page for updating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  request (Antrag)

  :param model: model
  :param form: form
  :param success_message: custom success message
  :param request_workflow: request workflow informations
  """

  model = CleanupEventRequest
  # override RequestMixin form
  form = ObjectForm
  # override RequestMixin success message
  success_message = ObjectUpdateView.success_message
  # empty workflow
  request_workflow = {}

  def form_invalid(self, form, **kwargs):
    """
    re-opens passed form if it is not valid
    (purpose: keep original referer)

    :param form: form
    :return: passed form if it is not valid
    """
    context_data = self.get_context_data(form=form)
    form.data = form.data.copy()
    context_data['cancel_url'] = form.data.get('original_referer', None)
    return self.render_to_response(context_data)

  def form_valid(self, form):
    """
    sends HTTP response if passed form is valid

    :param form: form
    :return: HTTP response if passed form is valid
    """
    old_instance = self.get_object()
    # delay necessary to allow automatic field contents to populate
    instance = form.save(commit=False)
    instance.full_clean()
    instance.save()
    # on every status change: send email to inform original requester
    if old_instance.status.name != instance.status.name:
      send_cleanupeventrequest_email(
        request=self.request,
        email_key='CLEANUPEVENTREQUEST_TO-REQUESTER_STATUS-CHANGED',
        curr_object=instance,
        recipient_list=[instance.requester.email]
      )
    return super().form_valid(form)

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add to context: authorative hint
    context['authorative'] = True
    # add to context: hidden and disabled fields
    context['hidden_fields'] = ['requester']
    context['disabled_fields'] = []
    # add to context: URLs
    context['cancel_url'] = get_referer_url(
      referer=get_referer(self.request),
      fallback='antragsmanagement:index'
    )
    # add permissions related context elements:
    # set authority permissions as necessary permissions
    context = add_permissions_context_elements(context, self.request.user, AUTHORITIES)
    return context

  def get_initial(self):
    """
    conditionally sets initial field values for this view

    :return: dictionary with initial field values for this view
    """
    # override RequestMixin method so that no field is pre-set
    return

  def get_success_url(self):
    """
    defines the URL called in case of successful request

    :return: URL called in case of successful request
    """
    referer = self.request.POST.get('original_referer', '')
    if 'table' in referer:
      return reverse('antragsmanagement:cleanupeventrequest_table')
    elif 'map' in referer:
      return reverse('antragsmanagement:cleanupeventrequest_map')
    return reverse('antragsmanagement:index')


class CleanupEventEventMixin(RequestFollowUpMixin):
  """
  mixin for form page for creating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  event (Aktion)

  :param model: model
  :param form: form
  :param error_message: custom error message
  :param cancel_message: custom cancel message
  :param request_workflow: request workflow informations
  :param request_field: request field
  :param request_model: request model
  """

  model = CleanupEventEvent
  form = CleanupEventEventForm
  error_message = 'Antrag auf Müllsammelaktion existiert nicht!'
  cancel_message = '<strong>Antrag auf Müllsammelaktion</strong> abgebrochen'
  request_workflow = {
    'steps': 5,
    'current_step': 2
  }
  request_field = 'cleanupevent_request'
  request_model = CleanupEventRequest

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add to context: URLs
    viewname = 'antragsmanagement:anonymous_cleanupeventrequest_update'
    if self.request.user.is_authenticated:
      viewname = 'antragsmanagement:cleanupeventrequest_update'
    context['back_url'] = reverse(
      viewname=viewname, kwargs={'pk': self.request.session.get('request_id', None)}
    )
    # add to context: map layer to additionally activate
    context['activate_map_layer'] = 'Bewirtschaftungskataster'
    return context

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


class CleanupEventEventCreateView(CleanupEventEventMixin, ObjectCreateView):
  """
  view for workflow page for creating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  event (Aktion)
  """

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


class CleanupEventEventUpdateView(CleanupEventEventMixin, ObjectUpdateView):
  """
  view for workflow page for updating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  event (Aktion)

  :param success_message: custom success message
  """

  success_message = 'Antragsdaten erfolgreich aktualisiert!'

  def get_initial(self):
    """
    conditionally sets initial field values for this view

    :return: dictionary with initial field values for this view
    """
    return clean_initial_field_values(
      fields=self.model._meta.get_fields(),
      model=self.model,
      curr_obj=self.object
    )

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


class CleanupEventEventAuthorativeUpdateView(RequestFollowUpAuthorativeMixin,
                                             CleanupEventEventMixin, ObjectUpdateView):
  """
  view for authorative form page for updating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  event (Aktion)
  """

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add to context: GeoJSONified geometries of venue place, container place, and dump place
    other_geometries = []
    request_id = self.object.cleanupevent_request.pk
    cleanupeventvenue_geometry = get_corresponding_cleanupeventrequest_geometry(
      request_id=request_id, model=CleanupEventVenue, text='zugehöriger<br>Treffpunkt')
    if cleanupeventvenue_geometry:
      other_geometries.append(cleanupeventvenue_geometry)
    cleanupeventcontainer_geometry = get_corresponding_cleanupeventrequest_geometry(
      request_id=request_id, model=CleanupEventContainer, text='zugehöriger<br>Containerstandort')
    if cleanupeventcontainer_geometry:
      other_geometries.append(cleanupeventcontainer_geometry)
    cleanupeventdump_geometry = get_corresponding_cleanupeventrequest_geometry(
      request_id=request_id, model=CleanupEventDump, text='zugehöriger<br>Müllablageplatz')
    if cleanupeventdump_geometry:
      other_geometries.append(cleanupeventdump_geometry)
    if other_geometries:
      context['other_geometries'] = other_geometries
    return context


class CleanupEventVenueMixin(RequestFollowUpMixin):
  """
  mixin for form page for creating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  venue (Treffpunkt)

  :param model: model
  :param error_message: custom error message
  :param cancel_message: custom cancel message
  :param request_workflow: request workflow informations
  :param request_field: request field
  :param request_model: request model
  """

  model = CleanupEventVenue
  error_message = 'Antrag auf Müllsammelaktion existiert nicht!'
  cancel_message = '<strong>Antrag auf Müllsammelaktion</strong> abgebrochen'
  request_workflow = {
    'steps': 5,
    'current_step': 3
  }
  request_field = 'cleanupevent_request'
  request_model = CleanupEventRequest

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add to context: URLs
    viewname = 'antragsmanagement:anonymous_cleanupeventevent_update'
    if self.request.user.is_authenticated:
      viewname = 'antragsmanagement:cleanupeventevent_update'
    context['back_url'] = reverse(
      viewname=viewname, kwargs={'pk': self.request.session.get('cleanupeventevent_id', None)}
    )
    # add to context: GeoJSONified geometry of event area
    cleanupeventevent_geometry = get_corresponding_cleanupeventrequest_geometry(
      request_id=self.request.session.get('request_id', None),
      model=CleanupEventEvent,
      text='Fläche<br>aus Schritt 2'
    )
    if cleanupeventevent_geometry:
      context['other_geometries'] = cleanupeventevent_geometry
    return context

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


class CleanupEventVenueCreateView(CleanupEventVenueMixin, ObjectCreateView):
  """
  view for workflow page for creating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  venue (Treffpunkt)
  """

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


class CleanupEventVenueUpdateView(CleanupEventVenueMixin, ObjectUpdateView):
  """
  view for workflow page for updating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  venue (Treffpunkt)

  :param success_message: custom success message
  """

  success_message = 'Antragsdaten erfolgreich aktualisiert!'

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


class CleanupEventVenueAuthorativeUpdateView(RequestFollowUpAuthorativeMixin,
                                             CleanupEventVenueMixin, ObjectUpdateView):
  """
  view for authorative form page for updating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  venue (Treffpunkt)
  """

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add to context: GeoJSONified geometries of event area, container place, and dump place
    other_geometries = []
    request_id = self.object.cleanupevent_request.pk
    cleanupeventevent_geometry = get_corresponding_cleanupeventrequest_geometry(
      request_id=request_id, model=CleanupEventEvent, text='zugehörige<br>Fläche')
    if cleanupeventevent_geometry:
      other_geometries.append(cleanupeventevent_geometry)
    cleanupeventcontainer_geometry = get_corresponding_cleanupeventrequest_geometry(
      request_id=request_id, model=CleanupEventContainer, text='zugehöriger<br>Containerstandort')
    if cleanupeventcontainer_geometry:
      other_geometries.append(cleanupeventcontainer_geometry)
    cleanupeventdump_geometry = get_corresponding_cleanupeventrequest_geometry(
      request_id=request_id, model=CleanupEventDump, text='zugehöriger<br>Müllablageplatz')
    if cleanupeventdump_geometry:
      other_geometries.append(cleanupeventdump_geometry)
    if other_geometries:
      context['other_geometries'] = other_geometries
    return context


class CleanupEventDetailsMixin(RequestFollowUpMixin):
  """
  mixin for form page for creating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  details (Detailangaben)

  :param model: model
  :param form: form
  :param error_message: custom error message
  :param cancel_message: custom cancel message
  :param request_workflow: request workflow informations
  :param request_field: request field
  :param request_model: request model
  """

  model = CleanupEventDetails
  form = CleanupEventDetailsForm
  error_message = 'Antrag auf Müllsammelaktion existiert nicht!'
  cancel_message = '<strong>Antrag auf Müllsammelaktion</strong> abgebrochen'
  request_workflow = {
    'steps': 5,
    'current_step': 4
  }
  request_field = 'cleanupevent_request'
  request_model = CleanupEventRequest

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add to context: URLs
    viewname = 'antragsmanagement:anonymous_cleanupeventvenue_update'
    if self.request.user.is_authenticated:
      viewname = 'antragsmanagement:cleanupeventvenue_update'
    context['back_url'] = reverse(
      viewname=viewname, kwargs={'pk': self.request.session.get('cleanupeventvenue_id', None)}
    )
    return context

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


class CleanupEventDetailsCreateView(CleanupEventDetailsMixin, ObjectCreateView):
  """
  view for workflow page for creating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  details (Detailangaben)
  """

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


class CleanupEventDetailsUpdateView(CleanupEventDetailsMixin, ObjectUpdateView):
  """
  view for workflow page for updating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  details (Detailangaben)

  :param success_message: custom success message
  """

  success_message = 'Antragsdaten erfolgreich aktualisiert!'

  def get_success_url(self):
    """
    defines the URL called in case of successful request

    :return: URL called in case of successful request
    """
    return reverse('antragsmanagement:cleanupeventcontainer_decision')


class CleanupEventDetailsAuthorativeUpdateView(RequestFollowUpAuthorativeMixin,
                                               CleanupEventDetailsMixin, ObjectUpdateView):
  """
  view for authorative form page for updating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  details (Detailangaben)
  """


class CleanupEventContainerDecisionView(RequestFollowUpDecisionMixin, TemplateView):
  """
  view for workflow decision page in terms of object
  for request type clean-up events (Müllsammelaktionen):
  container (Container)

  :param model: model
  :param error_message: custom error message
  :param cancel_message: custom cancel message
  :param success_message: custom success message
  :param request_workflow: request workflow informations
  :param decision_text: decision text to show on the page
  """

  model = CleanupEventContainer
  error_message = 'Antrag auf Müllsammelaktion existiert nicht!'
  cancel_message = '<strong>Antrag auf Müllsammelaktion</strong> abgebrochen'
  success_message = '<strong>Antrag auf Müllsammelaktion</strong> erfolgreich gespeichert!'
  request_workflow = {
    'steps': 5,
    'current_step': 5
  }
  decision_text = 'Ist ein Container für die Müllsammelaktion erforderlich? Falls ja, '
  decision_text += 'klicken Sie bitte auf <em>ja,</em> falls nicht, klicken Sie bitte auf '
  decision_text += '<em>nein,</em> um den Antrag auf Müllsammelaktion direkt abzuschließen.'

  def post(self, request, *args, **kwargs):
    if 'cancel' in request.POST:
      if request.session.get('request_id', None):
        try:
          request_object = get_request(
            CleanupEventRequest,
            request.session.get('request_id', None),
            only_primary_key=False
          )
          request_object.delete()
          messages.warning(request, self.cancel_message)
        except CleanupEventRequest.DoesNotExist:
            raise Http404(self.error_message)
    else:
      curr_request = CleanupEventRequest.objects.get(pk=request.session.get('request_id', None))
      # send email to inform requester about new request
      send_cleanupeventrequest_email(
        request=request,
        email_key='CLEANUPEVENTREQUEST_TO-REQUESTER_NEW',
        curr_object=curr_request,
        recipient_list=[curr_request.requester.email]
      )
      if curr_request.responsibilities.exists():
        responsibilities = curr_request.responsibilities.all()
        # use list comprehension to get recipients
        # (i.e. the email addresses of all responsible authorities)
        recipient_list = [
          responsibility.email for responsibility in responsibilities
        ]
        # send email to inform responsible authorities about new request
        send_cleanupeventrequest_email(
          request=request,
          email_key='CLEANUPEVENTREQUEST_TO-AUTHORITIES_NEW',
          curr_object=curr_request,
          recipient_list=recipient_list
        )
        # additional messages if certain responsibilities exist
        additional_messages(responsibilities, self.request)
      messages.success(request, self.success_message)
    if request.user.is_authenticated:
      return redirect('antragsmanagement:index')
    else:
      return redirect('antragsmanagement:anonymous_index')

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add to context: URLs
    if self.request.user.is_authenticated:
      context['yes_url'] = reverse('antragsmanagement:cleanupeventcontainer_create')
      context['back_url'] = reverse(
        viewname='antragsmanagement:cleanupeventdetails_update',
        kwargs={'pk': self.request.session.get('cleanupeventdetails_id', None)}
      )
      context['cancel_url'] = reverse('antragsmanagement:index')
    else:
      context['yes_url'] = reverse('antragsmanagement:anonymous_cleanupeventcontainer_create')
      context['back_url'] = reverse(
        viewname='antragsmanagement:anonymous_cleanupeventdetails_update',
        kwargs={'pk': self.request.session.get('cleanupeventdetails_id', None)}
      )
      context['cancel_url'] = reverse('antragsmanagement:anonymous_index')
    return context


class CleanupEventContainerMixin(RequestFollowUpMixin):
  """
  mixin for form page for creating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  container (Container)

  :param model: model
  :param form: form
  :param error_message: custom error message
  :param cancel_message: custom cancel message
  :param success_message: custom success message
  :param request_workflow: request workflow informations
  :param request_field: request field
  :param request_model: request model
  """

  model = CleanupEventContainer
  form = CleanupEventContainerForm
  error_message = 'Antrag auf Müllsammelaktion existiert nicht!'
  cancel_message = '<strong>Antrag auf Müllsammelaktion</strong> abgebrochen'
  success_message = '<strong>Antrag auf Müllsammelaktion</strong> erfolgreich gespeichert!'
  request_workflow = {
    'steps': 5,
    'current_step': 5
  }
  request_field = 'cleanupevent_request'
  request_model = CleanupEventRequest

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add to context: URLs
    viewname = 'antragsmanagement:anonymous_cleanupeventcontainer_decision'
    if self.request.user.is_authenticated:
      viewname = 'antragsmanagement:cleanupeventcontainer_decision'
    context['back_url'] = reverse(viewname)
    # add to context: GeoJSONified geometries of event area and venue place
    other_geometries = []
    request_id = self.request.session.get('request_id', None)
    cleanupeventevent_geometry = get_corresponding_cleanupeventrequest_geometry(
      request_id=request_id, model=CleanupEventEvent, text='Fläche<br>aus Schritt 2')
    if cleanupeventevent_geometry:
      other_geometries.append(cleanupeventevent_geometry)
    cleanupeventvenue_geometry = get_corresponding_cleanupeventrequest_geometry(
      request_id=request_id, model=CleanupEventVenue, text='Treffpunkt<br>aus Schritt 3')
    if cleanupeventvenue_geometry:
      other_geometries.append(cleanupeventvenue_geometry)
    if other_geometries:
      context['other_geometries'] = other_geometries
    return context


class CleanupEventContainerCreateView(CleanupEventContainerMixin, ObjectCreateView):
  """
  view for workflow page for creating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  container (Container)
  """

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
    request = instance.cleanupevent_request
    if request:
      # send email to inform requester about new request
      send_cleanupeventrequest_email(
        request=self.request,
        email_key='CLEANUPEVENTREQUEST_TO-REQUESTER_NEW',
        curr_object=request,
        recipient_list=[request.requester.email]
      )
      if request.responsibilities.exists():
        responsibilities = request.responsibilities.all()
        # use list comprehension to get get recipients
        # (i.e. the email addresses of all responsible authorities)
        recipient_list = [
          responsibility.email for responsibility in responsibilities
        ]
        # send email to inform responsible authorities about new request
        send_cleanupeventrequest_email(
          request=self.request,
          email_key='CLEANUPEVENTREQUEST_TO-AUTHORITIES_NEW',
          curr_object=request,
          recipient_list=recipient_list
        )
        # additional messages if certain responsibilities exist
        additional_messages(responsibilities, self.request)
    return super().form_valid(form)

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


class CleanupEventContainerAuthorativeCreateView(RequestFollowUpAuthorativeMixin,
                                                 CleanupEventContainerMixin, ObjectCreateView):
  """
  view for authorative form page for creating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  container (Container)

  :param success_message: custom success message
  """

  # override success message
  success_message = ObjectCreateView.success_message.replace('<strong>', 'zu <strong>')

  def form_invalid(self, form, **kwargs):
    """
    re-opens passed form if it is not valid
    (purpose: keep geometry and original referer)

    :param form: form
    :return: passed form if it is not valid
    """
    context_data = self.get_context_data(form=form)
    form.data = form.data.copy()
    context_data = geometry_keeper(form.data, self.model, context_data)
    context_data['cancel_url'] = form.data.get('original_referer', None)
    context_data['form'] = form
    return self.render_to_response(context_data)

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add to context: GeoJSONified geometries of event area, container place, and dump place
    other_geometries = []
    request_id = self.kwargs.get('request_id', None)
    cleanupeventevent_geometry = get_corresponding_cleanupeventrequest_geometry(
      request_id=request_id, model=CleanupEventEvent, text='zugehörige<br>Fläche')
    if cleanupeventevent_geometry:
      other_geometries.append(cleanupeventevent_geometry)
    cleanupeventvenue_geometry = get_corresponding_cleanupeventrequest_geometry(
      request_id=request_id, model=CleanupEventVenue, text='zugehöriger<br>Treffpunkt')
    if cleanupeventvenue_geometry:
      other_geometries.append(cleanupeventvenue_geometry)
    cleanupeventdump_geometry = get_corresponding_cleanupeventrequest_geometry(
      request_id=request_id, model=CleanupEventDump, text='zugehöriger<br>Müllablageplatz')
    if cleanupeventdump_geometry:
      other_geometries.append(cleanupeventdump_geometry)
    if other_geometries:
      context['other_geometries'] = other_geometries
    return context

  def get_initial(self):
    """
    conditionally sets initial field values for this view

    :return: dictionary with initial field values for this view
    """
    # get corresponding request object via ID passed as URL parameter
    # and set request to it
    if self.kwargs.get('request_id', None):
      return {
        'cleanupevent_request': get_request(
          CleanupEventRequest, self.kwargs.get('request_id', None))
      }
    return {}


class CleanupEventContainerAuthorativeUpdateView(RequestFollowUpAuthorativeMixin,
                                                 CleanupEventContainerMixin, ObjectUpdateView):
  """
  view for authorative form page for updating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  container (Container)
  """

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add to context: GeoJSONified geometries of event area, container place, and dump place
    other_geometries = []
    request_id = self.object.cleanupevent_request.pk
    cleanupeventevent_geometry = get_corresponding_cleanupeventrequest_geometry(
      request_id=request_id, model=CleanupEventEvent, text='zugehörige<br>Fläche')
    if cleanupeventevent_geometry:
      other_geometries.append(cleanupeventevent_geometry)
    cleanupeventvenue_geometry = get_corresponding_cleanupeventrequest_geometry(
      request_id=request_id, model=CleanupEventVenue, text='zugehöriger<br>Treffpunkt')
    if cleanupeventvenue_geometry:
      other_geometries.append(cleanupeventvenue_geometry)
    cleanupeventdump_geometry = get_corresponding_cleanupeventrequest_geometry(
      request_id=request_id, model=CleanupEventDump, text='zugehöriger<br>Müllablageplatz')
    if cleanupeventdump_geometry:
      other_geometries.append(cleanupeventdump_geometry)
    if other_geometries:
      context['other_geometries'] = other_geometries
    return context


class CleanupEventContainerDeleteView(RequestFollowUpDeleteMixin, ObjectDeleteView):
  """
  view for form page for deleting an instance of object
  for request type clean-up events (Müllsammelaktionen):
  container (Container)

  :param model: model
  """

  model = CleanupEventContainer


class CleanupEventDumpMixin(RequestFollowUpMixin):
  """
  mixin for form page for creating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  dump (Müllablageplatz)

  :param model: model
  :param request_field: request field
  :param request_model: request model
  """

  model = CleanupEventDump
  request_field = 'cleanupevent_request'
  request_model = CleanupEventRequest

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add to context: GeoJSONified geometries of event area, container place, and dump place
    other_geometries = []
    if self.object:
      request_id = self.object.cleanupevent_request.pk
    else:
      request_id = self.kwargs.get('request_id', None)
    cleanupeventevent_geometry = get_corresponding_cleanupeventrequest_geometry(
      request_id=request_id, model=CleanupEventEvent, text='zugehörige<br>Fläche')
    if cleanupeventevent_geometry:
      other_geometries.append(cleanupeventevent_geometry)
    cleanupeventvenue_geometry = get_corresponding_cleanupeventrequest_geometry(
      request_id=request_id, model=CleanupEventVenue, text='zugehöriger<br>Treffpunkt')
    if cleanupeventvenue_geometry:
      other_geometries.append(cleanupeventvenue_geometry)
    cleanupeventcontainer_geometry = get_corresponding_cleanupeventrequest_geometry(
      request_id=request_id, model=CleanupEventContainer, text='zugehöriger<br>Containerstandort')
    if cleanupeventcontainer_geometry:
      other_geometries.append(cleanupeventcontainer_geometry)
    if other_geometries:
      context['other_geometries'] = other_geometries
    return context


class CleanupEventDumpAuthorativeCreateView(RequestFollowUpAuthorativeMixin,
                                            CleanupEventDumpMixin, ObjectCreateView):
  """
  view for authorative form page for creating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  dump (Müllablageplatz)

  :param success_message: custom success message
  """

  # override success message
  success_message = ObjectCreateView.success_message.replace('<strong>', 'zu <strong>')

  def form_invalid(self, form, **kwargs):
    """
    re-opens passed form if it is not valid
    (purpose: keep geometry and original referer)

    :param form: form
    :return: passed form if it is not valid
    """
    context_data = self.get_context_data(form=form)
    form.data = form.data.copy()
    context_data = geometry_keeper(form.data, self.model, context_data)
    context_data['cancel_url'] = form.data.get('original_referer', None)
    context_data['form'] = form
    return self.render_to_response(context_data)

  def get_initial(self):
    """
    conditionally sets initial field values for this view

    :return: dictionary with initial field values for this view
    """
    # get corresponding request object via ID passed as URL parameter
    # and set request to it
    if self.kwargs.get('request_id', None):
      return {
        'cleanupevent_request': get_request(
          CleanupEventRequest, self.kwargs.get('request_id', None))
      }
    return {}


class CleanupEventDumpAuthorativeUpdateView(RequestFollowUpAuthorativeMixin,
                                            CleanupEventDumpMixin, ObjectUpdateView):
  """
  view for authorative form page for updating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  dump (Müllablageplatz)
  """


class CleanupEventDumpDeleteView(RequestFollowUpDeleteMixin, ObjectDeleteView):
  """
  view for form page for deleting an instance of object
  for request type clean-up events (Müllsammelaktionen):
  dump (Müllablageplatz)

  :param model: model
  """

  model = CleanupEventDump


#
# anonymous
#

@method_decorator(csrf_protect, name='dispatch')
@method_decorator(ratelimit(key='ip', rate='5/m', method='POST'), name='dispatch')
class RequesterCreateAnonymousView(RequesterCreateView):
  """
  view for anonymous form page for creating an instance of general object:
  requester (Antragsteller:in)
  """


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(ratelimit(key='ip', rate='5/m', method='POST'), name='dispatch')
class RequesterUpdateAnonymousView(RequesterUpdateView):
  """
  view for form page for updating an instance of general object:
  requester (Antragsteller:in)
  """


class CleanupEventRequestDataAnonymousView(JsonView):
  """
  view for anonymously composing data out of instances of object
  for request type clean-up events (Müllsammelaktionen):
  request (Antrag)
  """

  def get_context_data(self, **kwargs):
    """
    returns GeoJSON feature collection

    :param kwargs:
    :return: GeoJSON feature collection
    """
    # get all approved requests
    queryset = CleanupEventRequest.objects.prefetch_related(
      'cleanupeventevent'
    ).filter(
      status__ordinal=2
    )
    queryset = queryset.values(
      'id',
      'cleanupeventevent__from_date',
      'cleanupeventevent__to_date'
    )
    # declare empty GeoJSON feature collection
    feature_collection = {
      'type': 'FeatureCollection',
      'features': []
    }
    # handle requests
    for item in queryset:
      # request must be scheduled in future
      from_date, to_date = item['cleanupeventevent__from_date'], item['cleanupeventevent__to_date']
      if (
        from_date and from_date >= date.today()
      ) or (
        to_date and to_date >= date.today()
      ):
        # add GeoJSON feature to GeoJSON feature collection
        request = get_cleanupeventrequest_anonymous_api_feature(item['id'])
        if request:
          feature_collection['features'].append(request)
    return JsonResponse(
      feature_collection,
      json_dumps_params={'indent': 2, 'ensure_ascii': False},
      content_type='application/json; charset=utf-8'
    )


class CleanupEventRequestMapDataAnonymousView(JsonView):
  """
  view for anonymously composing map data out of one instance of object
  for request type clean-up events (Müllsammelaktionen):
  request (Antrag)
  """

  def get_context_data(self, **kwargs):
    """
    returns GeoJSON feature collection

    :param kwargs:
    :return: GeoJSON feature collection
    """
    request_id = self.kwargs.get('request_id', None)
    # get request
    request = CleanupEventRequest.objects.filter(pk=request_id).first()
    # declare empty GeoJSON feature collection
    feature_collection = {
      'type': 'FeatureCollection',
      'features': []
    }
    # handle request
    if request:
      # add GeoJSON feature for event to GeoJSON feature collection
      event = get_cleanupeventrequest_anonymous_feature(
        curr_request=request,
        curr_type='event'
      )
      if event:
        feature_collection['features'].append(event)
      # add GeoJSON feature for venue to GeoJSON feature collection
      venue = get_cleanupeventrequest_anonymous_feature(
        curr_request=request,
        curr_type='venue'
      )
      if venue:
        feature_collection['features'].append(venue)
      # add GeoJSON feature for container to GeoJSON feature collection
      container = get_cleanupeventrequest_anonymous_feature(
        curr_request=request,
        curr_type='container'
      )
      if container:
        feature_collection['features'].append(container)
      # add GeoJSON feature for dump to GeoJSON feature collection
      container = get_cleanupeventrequest_anonymous_feature(
        curr_request=request,
        curr_type='dump'
      )
      if container:
        feature_collection['features'].append(container)
    return feature_collection


class CleanupEventRequestMapAnonymousView(TemplateView):
  """
  view for anonymous map page for one instance of object
  for request type clean-up events (Müllsammelaktionen):
  request (Antrag)

  :param model: template model
  :param template_name: template name
  :param map_data_view_name: name of view for composing map data out of instances
  :param icon_name: icon name
  """

  model = CleanupEventRequest
  template_name = 'antragsmanagement/anonymous_map_request.html'
  map_data_view_name = 'antragsmanagement:anonymous_cleanupeventrequest_mapdata'
  icon_name = 'cleanupeventrequest'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    request_id = self.kwargs.get('request_id', None)
    # add user agent related context elements
    context = add_useragent_context_elements(context, self.request)
    # add model related context elements
    context['model_verbose_name'] = self.model._meta.verbose_name
    request = self.model.objects.filter(pk=request_id).first()
    if request:
      context['object_title'] = str(request)
    # add map related context elements
    context['LEAFLET_CONFIG'] = settings.LEAFLET_CONFIG
    context['mapdata_url'] = reverse(
      viewname=self.map_data_view_name,
      kwargs={'request_id': request_id}
    )
    # add to context: icon
    context['icon'] = self.icon_name
    return context


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(ratelimit(key='ip', rate='5/m', method='POST'), name='dispatch')
class CleanupEventRequestCreateAnonymousView(CleanupEventRequestCreateView):
  """
  view for anonymous workflow page for creating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  request (Antrag)
  """


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(ratelimit(key='ip', rate='5/m', method='POST'), name='dispatch')
class CleanupEventRequestUpdateAnonymousView(CleanupEventRequestUpdateView):
  """
  view for anonymous workflow page for updating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  request (Antrag)
  """

  def get_success_url(self):
    """
    defines the URL called in case of successful request

    :return: URL called in case of successful request
    """
    if self.request.session.get('cleanupeventevent_id', None):
      return reverse(
        viewname='antragsmanagement:anonymous_cleanupeventevent_update',
        kwargs={'pk': self.request.session['cleanupeventevent_id']}
      )
    else:
      return reverse('antragsmanagement:anonymous_cleanupeventevent_create')


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(ratelimit(key='ip', rate='5/m', method='POST'), name='dispatch')
class CleanupEventEventCreateAnonymousView(CleanupEventEventCreateView):
  """
  view for anonymous workflow page for creating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  event (Aktion)
  """


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(ratelimit(key='ip', rate='5/m', method='POST'), name='dispatch')
class CleanupEventEventUpdateAnonymousView(CleanupEventEventUpdateView):
  """
  view for anonymous workflow page for updating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  event (Aktion)
  """

  def get_success_url(self):
    """
    defines the URL called in case of successful request

    :return: URL called in case of successful request
    """
    if self.request.session.get('cleanupeventvenue_id', None):
      return reverse(
        viewname='antragsmanagement:anonymous_cleanupeventvenue_update',
        kwargs={'pk': self.request.session['cleanupeventvenue_id']}
      )
    else:
      return reverse('antragsmanagement:anonymous_cleanupeventvenue_create')


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(ratelimit(key='ip', rate='5/m', method='POST'), name='dispatch')
class CleanupEventVenueCreateAnonymousView(CleanupEventVenueCreateView):
  """
  view for anonymous workflow page for creating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  venue (Treffpunkt)
  """


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(ratelimit(key='ip', rate='5/m', method='POST'), name='dispatch')
class CleanupEventVenueUpdateAnonymousView(CleanupEventVenueUpdateView):
  """
  view for anonymous workflow page for updating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  venue (Treffpunkt)
  """

  def get_success_url(self):
    """
    defines the URL called in case of successful request

    :return: URL called in case of successful request
    """
    if self.request.session.get('cleanupeventdetails_id', None):
      return reverse(
        viewname='antragsmanagement:anonymous_cleanupeventdetails_update',
        kwargs={'pk': self.request.session['cleanupeventdetails_id']}
      )
    else:
      return reverse('antragsmanagement:anonymous_cleanupeventdetails_create')


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(ratelimit(key='ip', rate='5/m', method='POST'), name='dispatch')
class CleanupEventDetailsCreateAnonymousView(CleanupEventDetailsCreateView):
  """
  view for anonymous workflow page for creating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  details (Detailangaben)
  """


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(ratelimit(key='ip', rate='5/m', method='POST'), name='dispatch')
class CleanupEventDetailsUpdateAnonymousView(CleanupEventDetailsUpdateView):
  """
  view for anonymous workflow page for updating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  details (Detailangaben)
  """

  def get_success_url(self):
    """
    defines the URL called in case of successful request

    :return: URL called in case of successful request
    """
    return reverse('antragsmanagement:anonymous_cleanupeventcontainer_decision')


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(ratelimit(key='ip', rate='5/m', method='POST'), name='dispatch')
class CleanupEventContainerDecisionAnonymousView(CleanupEventContainerDecisionView):
  """
  view for anonymous workflow decision page in terms of object
  for request type clean-up events (Müllsammelaktionen):
  container (Container)
  """


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(ratelimit(key='ip', rate='5/m', method='POST'), name='dispatch')
class CleanupEventContainerCreateAnonymousView(CleanupEventContainerCreateView):
  """
  view for anonymous workflow page for creating an instance of object
  for request type clean-up events (Müllsammelaktionen):
  container (Container)
  """
