from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy
from rest_framework import routers

from antragsmanagement.views.views import IndexView, AuthorityTableDataView, AuthorityTableView, \
  AuthorityUpdateView, EmailTableDataView, EmailTableView, EmailUpdateView, RequesterCreateView, \
  RequesterUpdateView, CleanupEventRequestCreateView, CleanupEventRequestUpdateView, \
  CleanupEventEventCreateView, CleanupEventEventUpdateView, CleanupEventVenueCreateView, \
  CleanupEventVenueUpdateView, CleanupEventDetailsCreateView, CleanupEventDetailsUpdateView, \
  CleanupEventContainerCreateView

router = routers.DefaultRouter()

api_urlpatterns = router.urls

app_name = 'antragsmanagement'


urlpatterns = [
  # main page
  path(
    '',
    view=login_required(IndexView.as_view()),
    name='index'
  ),
  # composing table data out of instances of general object:
  # authority (Behörde)
  path(
    'authority/tabledata',
    view=login_required(AuthorityTableDataView.as_view()),
    name='authority_tabledata'
  ),
  # table page for instances of general object:
  # authority (Behörde)
  path(
    'authority/table',
    view=login_required(AuthorityTableView.as_view()),
    name='authority_table'
  ),
  # form page for updating an instance of general object:
  # authority (Behörde)
  path(
    'authority/update/<pk>',
    view=login_required(AuthorityUpdateView.as_view(
      success_url=reverse_lazy('antragsmanagement:authority_table')
    )),
    name='authority_update'
  ),
  # composing table data out of instances of general object:
  # email (E-Mail)
  path(
    'email/tabledata',
    view=login_required(EmailTableDataView.as_view()),
    name='email_tabledata'
  ),
  # table page for instances of general object:
  # email (E-Mail)
  path(
    'email/table',
    view=login_required(EmailTableView.as_view()),
    name='email_table'
  ),
  # form page for updating an instance of general object:
  # email (E-Mail)
  path(
    'email/update/<pk>',
    view=login_required(EmailUpdateView.as_view(
      success_url=reverse_lazy('antragsmanagement:email_table')
    )),
    name='email_update'
  ),
  # form page for creating an instance of general object:
  # requester (Antragsteller:in)
  path(
    'requester/create',
    view=login_required(RequesterCreateView.as_view(
      success_url=reverse_lazy('antragsmanagement:index')
    )),
    name='requester_create'
  ),
  # form page for updating an instance of general object:
  # requester (Antragsteller:in)
  path(
    'requester/update/<pk>',
    view=login_required(RequesterUpdateView.as_view(
      success_url=reverse_lazy('antragsmanagement:index')
    )),
    name='requester_update'
  ),
  # form page for creating an instance of object for request type clean-up events
  # (Müllsammelaktionen):
  # request (Antrag)
  path(
    'cleanupeventrequest/create',
    view=login_required(CleanupEventRequestCreateView.as_view(
      success_url=reverse_lazy('antragsmanagement:cleanupeventevent_create')
    )),
    name='cleanupeventrequest_create'
  ),
  # form page for updating an instance of object for request type clean-up events
  # (Müllsammelaktionen):
  # request (Antrag)
  path(
    'cleanupeventrequest/update/<pk>',
    view=login_required(CleanupEventRequestUpdateView.as_view()),
    name='cleanupeventrequest_update'
  ),
  # form page for creating an instance of object for request type clean-up events
  # (Müllsammelaktionen):
  # event (Aktion)
  path(
    'cleanupeventevent/create',
    view=login_required(CleanupEventEventCreateView.as_view(
      success_url=reverse_lazy('antragsmanagement:cleanupeventvenue_create')
    )),
    name='cleanupeventevent_create'
  ),
  # form page for updating an instance of object for request type clean-up events
  # (Müllsammelaktionen):
  # event (Aktion)
  path(
    'cleanupeventevent/update/<pk>',
    view=login_required(CleanupEventEventUpdateView.as_view()),
    name='cleanupeventevent_update'
  ),
  # form page for creating an instance of object for request type clean-up events
  # (Müllsammelaktionen):
  # venue (Treffpunkt)
  path(
    'cleanupeventvenue/create',
    view=login_required(CleanupEventVenueCreateView.as_view(
      success_url=reverse_lazy('antragsmanagement:cleanupeventdetails_create')
    )),
    name='cleanupeventvenue_create'
  ),
  # form page for updating an instance of object for request type clean-up events
  # (Müllsammelaktionen):
  # venue (Treffpunkt)
  path(
    'cleanupeventvenue/update/<pk>',
    view=login_required(CleanupEventVenueUpdateView.as_view()),
    name='cleanupeventvenue_update'
  ),
  # form page for creating an instance of object for request type clean-up events
  # (Müllsammelaktionen):
  # details (Detailangaben)
  path(
    'cleanupeventdetails/create',
    view=login_required(CleanupEventDetailsCreateView.as_view(
      success_url=reverse_lazy('antragsmanagement:cleanupeventcontainer_create')
    )),
    name='cleanupeventdetails_create'
  ),
  # form page for updating an instance of object for request type clean-up events
  # (Müllsammelaktionen):
  # details (Detailangaben)
  path(
    'cleanupeventdetails/update/<pk>',
    view=login_required(CleanupEventDetailsUpdateView.as_view(
      success_url=reverse_lazy('antragsmanagement:cleanupeventcontainer_create')
    )),
    name='cleanupeventdetails_update'
  ),
  # form page for creating an instance of object for request type clean-up events
  # (Müllsammelaktionen):
  # container (Container)
  path(
    'cleanupeventcontainer/create',
    view=login_required(CleanupEventContainerCreateView.as_view(
      success_url=reverse_lazy('antragsmanagement:index')
    )),
    name='cleanupeventcontainer_create'
  )
]
