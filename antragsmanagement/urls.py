from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy
from rest_framework import routers

from .views import IndexView, AuthorityTableDataView, AuthorityTableView, \
  AuthorityUpdateView, EmailTableDataView, EmailTableView, EmailUpdateView, RequesterCreateView, \
  RequesterUpdateView, CleanupEventRequestTableDataView, CleanupEventRequestTableView, \
  CleanupEventRequestMapDataView, CleanupEventRequestMapView, \
  CleanupEventRequestCreateView, CleanupEventRequestUpdateView, \
  CleanupEventRequestAuthorativeUpdateView, CleanupEventEventCreateView, \
  CleanupEventEventUpdateView, CleanupEventVenueCreateView, CleanupEventVenueUpdateView, \
  CleanupEventDetailsCreateView, CleanupEventDetailsUpdateView, \
  CleanupEventContainerDecisionView, CleanupEventContainerCreateView

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
  # composing table data out of instances of object
  # for request type clean-up events (Müllsammelaktionen):
  # request (Antrag)
  path(
    'ce-request/tabledata',
    view=login_required(CleanupEventRequestTableDataView.as_view()),
    name='cleanupeventrequest_tabledata'
  ),
  # table page for instances of object
  # for request type clean-up events (Müllsammelaktionen):
  # request (Antrag)
  path(
    'ce-request/table',
    view=login_required(CleanupEventRequestTableView.as_view()),
    name='cleanupeventrequest_table'
  ),
  # composing map data out of instances of object
  # for request type clean-up events (Müllsammelaktionen):
  # request (Antrag)
  path(
    'ce-request/mapdata',
    view=login_required(CleanupEventRequestMapDataView.as_view()),
    name='cleanupeventrequest_mapdata'
  ),
  # map page for instances of object
  # for request type clean-up events (Müllsammelaktionen):
  # request (Antrag)
  path(
    'ce-request/map',
    view=login_required(CleanupEventRequestMapView.as_view()),
    name='cleanupeventrequest_map'
  ),
  # workflow page for creating an instance of object
  # for request type clean-up events (Müllsammelaktionen):
  # request (Antrag)
  path(
    'ce-request/create',
    view=login_required(CleanupEventRequestCreateView.as_view(
      success_url=reverse_lazy('antragsmanagement:cleanupeventevent_create')
    )),
    name='cleanupeventrequest_create'
  ),
  # workflow page for updating an instance of object
  # for request type clean-up events (Müllsammelaktionen):
  # request (Antrag)
  path(
    'ce-request/update/<pk>',
    view=login_required(CleanupEventRequestUpdateView.as_view()),
    name='cleanupeventrequest_update'
  ),
  # authorative form page for updating an instance of object
  # for request type clean-up events (Müllsammelaktionen):
  # request (Antrag)
  path(
    'ce-request/authorative/update/<pk>',
    view=login_required(CleanupEventRequestAuthorativeUpdateView.as_view()),
    name='cleanupeventrequest_authorative_update'
  ),
  # workflow page for creating an instance of object
  # for request type clean-up events (Müllsammelaktionen):
  # event (Aktion)
  path(
    'ce-request/event/create',
    view=login_required(CleanupEventEventCreateView.as_view(
      success_url=reverse_lazy('antragsmanagement:cleanupeventvenue_create')
    )),
    name='cleanupeventevent_create'
  ),
  # workflow page for updating an instance of object
  # for request type clean-up events (Müllsammelaktionen):
  # event (Aktion)
  path(
    'ce-request/event/update/<pk>',
    view=login_required(CleanupEventEventUpdateView.as_view()),
    name='cleanupeventevent_update'
  ),
  # workflow page for creating an instance of object
  # for request type clean-up events (Müllsammelaktionen):
  # venue (Treffpunkt)
  path(
    'ce-request/venue/create',
    view=login_required(CleanupEventVenueCreateView.as_view(
      success_url=reverse_lazy('antragsmanagement:cleanupeventdetails_create')
    )),
    name='cleanupeventvenue_create'
  ),
  # workflow page for updating an instance of object
  # for request type clean-up events (Müllsammelaktionen):
  # venue (Treffpunkt)
  path(
    'ce-request/venue/update/<pk>',
    view=login_required(CleanupEventVenueUpdateView.as_view()),
    name='cleanupeventvenue_update'
  ),
  # workflow page for creating an instance of object
  # for request type clean-up events (Müllsammelaktionen):
  # details (Detailangaben)
  path(
    'ce-request/details/create',
    view=login_required(CleanupEventDetailsCreateView.as_view(
      success_url=reverse_lazy('antragsmanagement:cleanupeventcontainer_decision')
    )),
    name='cleanupeventdetails_create'
  ),
  # workflow page for updating an instance of object
  # for request type clean-up events (Müllsammelaktionen):
  # details (Detailangaben)
  path(
    'ce-request/details/update/<pk>',
    view=login_required(CleanupEventDetailsUpdateView.as_view()),
    name='cleanupeventdetails_update'
  ),
  # workflow decision page in terms of object
  # for request type clean-up events (Müllsammelaktionen):
  # container (Container)
  path(
    'ce-request/container/decision',
    view=login_required(CleanupEventContainerDecisionView.as_view()),
    name='cleanupeventcontainer_decision'
  ),
  # workflow page for creating an instance of object
  # for request type clean-up events (Müllsammelaktionen):
  # container (Container)
  path(
    'ce-request/container/create',
    view=login_required(CleanupEventContainerCreateView.as_view(
      success_url=reverse_lazy('antragsmanagement:index')
    )),
    name='cleanupeventcontainer_create'
  )
]
