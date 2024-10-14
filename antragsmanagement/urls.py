from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy
from rest_framework import routers

from .views import IndexView, AuthorityTableDataView, AuthorityTableView, \
  AuthorityUpdateView, EmailTableDataView, EmailTableView, EmailUpdateView, RequesterCreateView, \
  RequesterUpdateView, CleanupEventRequestTableDataView, CleanupEventRequestTableView, \
  CleanupEventRequestMapDataView, CleanupEventRequestMapView, \
  CleanupEventRequestCreateView, CleanupEventRequestUpdateView, \
  CleanupEventRequestAuthorativeUpdateView, CleanupEventEventCreateView, \
  CleanupEventEventUpdateView, CleanupEventEventAuthorativeUpdateView, \
  CleanupEventVenueCreateView, CleanupEventVenueUpdateView, \
  CleanupEventVenueAuthorativeUpdateView, CleanupEventDetailsCreateView, \
  CleanupEventDetailsUpdateView, CleanupEventDetailsAuthorativeUpdateView, \
  CleanupEventContainerDecisionView, CleanupEventContainerCreateView, \
  CleanupEventContainerAuthorativeCreateView, CleanupEventContainerAuthorativeUpdateView, \
  CleanupEventContainerDeleteView, CleanupEventDumpAuthorativeCreateView, \
  CleanupEventDumpAuthorativeUpdateView, CleanupEventDumpDeleteView, \
  RequesterCreateAnonymousView, RequesterUpdateAnonymousView, \
  CleanupEventRequestDataAnonymousView, CleanupEventRequestMapDataAnonymousView, \
  CleanupEventRequestMapAnonymousView, CleanupEventRequestCreateAnonymousView, \
  CleanupEventRequestUpdateAnonymousView, CleanupEventEventCreateAnonymousView, \
  CleanupEventEventUpdateAnonymousView, CleanupEventVenueCreateAnonymousView, \
  CleanupEventVenueUpdateAnonymousView, CleanupEventDetailsCreateAnonymousView, \
  CleanupEventDetailsUpdateAnonymousView, CleanupEventContainerDecisionAnonymousView, \
  CleanupEventContainerCreateAnonymousView

router = routers.DefaultRouter()

api_urlpatterns = router.urls

app_name = 'antragsmanagement'


urlpatterns = [
  #
  # URLs only accessible after login
  #
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
  # authorative form page for updating an instance of object
  # for request type clean-up events (Müllsammelaktionen):
  # event (Aktion)
  path(
    'ce-request/event/authorative/update/<pk>',
    view=login_required(CleanupEventEventAuthorativeUpdateView.as_view()),
    name='cleanupeventevent_authorative_update'
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
  # authorative form page for updating an instance of object
  # for request type clean-up events (Müllsammelaktionen):
  # venue (Treffpunkt)
  path(
    'ce-request/venue/authorative/update/<pk>',
    view=login_required(CleanupEventVenueAuthorativeUpdateView.as_view()),
    name='cleanupeventvenue_authorative_update'
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
  # authorative form page for updating an instance of object
  # for request type clean-up events (Müllsammelaktionen):
  # details (Detailangaben)
  path(
    'ce-request/details/authorative/update/<pk>',
    view=login_required(CleanupEventDetailsAuthorativeUpdateView.as_view()),
    name='cleanupeventdetails_authorative_update'
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
  ),
  # authorative form page for updating an instance of object
  # for request type clean-up events (Müllsammelaktionen):
  # container (Container)
  path(
    'ce-request/container/authorative/create/<request_id>',
    view=login_required(CleanupEventContainerAuthorativeCreateView.as_view()),
    name='cleanupeventcontainer_authorative_create'
  ),
  # authorative form page for updating an instance of object
  # for request type clean-up events (Müllsammelaktionen):
  # container (Container)
  path(
    'ce-request/container/authorative/update/<pk>',
    view=login_required(CleanupEventContainerAuthorativeUpdateView.as_view()),
    name='cleanupeventcontainer_authorative_update'
  ),
  # page for deleting an instance of object for request type clean-up events (Müllsammelaktionen):
  # container (Container)
  path(
    'ce-request/container/delete/<pk>',
    view=login_required(CleanupEventContainerDeleteView.as_view()),
    name='cleanupeventcontainer_delete'
  ),
  # authorative form page for updating an instance of object
  # for request type clean-up events (Müllsammelaktionen):
  # dump (Müllablageplatz)
  path(
    'ce-request/dump/authorative/create/<request_id>',
    view=login_required(CleanupEventDumpAuthorativeCreateView.as_view()),
    name='cleanupeventdump_authorative_create'
  ),
  # authorative form page for updating an instance of object
  # for request type clean-up events (Müllsammelaktionen):
  # dump (Müllablageplatz)
  path(
    'ce-request/dump/authorative/update/<pk>',
    view=login_required(CleanupEventDumpAuthorativeUpdateView.as_view()),
    name='cleanupeventdump_authorative_update'
  ),
  # page for deleting an instance of object for request type clean-up events (Müllsammelaktionen):
  # dump (Müllablageplatz)
  path(
    'ce-request/dump/delete/<pk>',
    view=login_required(CleanupEventDumpDeleteView.as_view()),
    name='cleanupeventdump_delete'
  ),
  #
  # URLs also accessible anonymously
  #
  # anonymous main page
  path(
    'public',
    view=IndexView.as_view(),
    name='anonymous_index'
  ),
  # anonymous form page for creating an instance of general object:
  # requester (Antragsteller:in)
  path(
    'public/requester/create',
    view=RequesterCreateAnonymousView.as_view(
      success_url=reverse_lazy('antragsmanagement:anonymous_index')
    ),
    name='anonymous_requester_create'
  ),
  # anonymous form page for updating an instance of general object:
  # requester (Antragsteller:in)
  path(
    'public/requester/update/<pk>',
    view=RequesterUpdateAnonymousView.as_view(
      success_url=reverse_lazy('antragsmanagement:anonymous_index')
    ),
    name='anonymous_requester_update'
  ),
  # anonymously composing data out of instances of object
  # for request type clean-up events (Müllsammelaktionen):
  # request (Antrag)
  path(
    'public/ce-request/data',
    view=CleanupEventRequestDataAnonymousView.as_view(),
    name='anonymous_cleanupeventrequest_data'
  ),
  # anonymously composing map data out of one instance of object
  # for request type clean-up events (Müllsammelaktionen):
  # request (Antrag)
  path(
    'public/ce-request/mapdata/<request_id>',
    view=CleanupEventRequestMapDataAnonymousView.as_view(),
    name='anonymous_cleanupeventrequest_mapdata'
  ),
  # anonymous map page for one instance of object
  # for request type clean-up events (Müllsammelaktionen):
  # request (Antrag)
  path(
    'public/ce-request/map/<request_id>',
    view=CleanupEventRequestMapAnonymousView.as_view(),
    name='anonymous_cleanupeventrequest_map'
  ),
  # anonymous workflow page for creating an instance of object
  # for request type clean-up events (Müllsammelaktionen):
  # request (Antrag)
  path(
    'public/ce-request/create',
    view=CleanupEventRequestCreateAnonymousView.as_view(
      success_url=reverse_lazy('antragsmanagement:anonymous_cleanupeventevent_create')
    ),
    name='anonymous_cleanupeventrequest_create'
  ),
  # anonymous workflow page for updating an instance of object
  # for request type clean-up events (Müllsammelaktionen):
  # request (Antrag)
  path(
    'public/ce-request/update/<pk>',
    view=CleanupEventRequestUpdateAnonymousView.as_view(),
    name='anonymous_cleanupeventrequest_update'
  ),
  # anonymous workflow page for creating an instance of object
  # for request type clean-up events (Müllsammelaktionen):
  # event (Aktion)
  path(
    'public/ce-request/event/create',
    view=CleanupEventEventCreateAnonymousView.as_view(
      success_url=reverse_lazy('antragsmanagement:anonymous_cleanupeventvenue_create')
    ),
    name='anonymous_cleanupeventevent_create'
  ),
  # anonymous workflow page for updating an instance of object
  # for request type clean-up events (Müllsammelaktionen):
  # event (Aktion)
  path(
    'public/ce-request/event/update/<pk>',
    view=CleanupEventEventUpdateAnonymousView.as_view(),
    name='anonymous_cleanupeventevent_update'
  ),
  # anonymous workflow page for creating an instance of object
  # for request type clean-up events (Müllsammelaktionen):
  # venue (Treffpunkt)
  path(
    'public/ce-request/venue/create',
    view=CleanupEventVenueCreateAnonymousView.as_view(
      success_url=reverse_lazy('antragsmanagement:anonymous_cleanupeventdetails_create')
    ),
    name='anonymous_cleanupeventvenue_create'
  ),
  # anonymous workflow page for updating an instance of object
  # for request type clean-up events (Müllsammelaktionen):
  # venue (Treffpunkt)
  path(
    'public/ce-request/venue/update/<pk>',
    view=CleanupEventVenueUpdateAnonymousView.as_view(),
    name='anonymous_cleanupeventvenue_update'
  ),
  # anonymous workflow page for creating an instance of object
  # for request type clean-up events (Müllsammelaktionen):
  # details (Detailangaben)
  path(
    'public/ce-request/details/create',
    view=CleanupEventDetailsCreateAnonymousView.as_view(
      success_url=reverse_lazy('antragsmanagement:anonymous_cleanupeventcontainer_decision')
    ),
    name='anonymous_cleanupeventdetails_create'
  ),
  # anonymous workflow page for updating an instance of object
  # for request type clean-up events (Müllsammelaktionen):
  # details (Detailangaben)
  path(
    'public/ce-request/details/update/<pk>',
    view=CleanupEventDetailsUpdateAnonymousView.as_view(),
    name='anonymous_cleanupeventdetails_update'
  ),
  # anonymous workflow decision page in terms of object
  # for request type clean-up events (Müllsammelaktionen):
  # container (Container)
  path(
    'public/ce-request/container/decision',
    view=CleanupEventContainerDecisionAnonymousView.as_view(),
    name='anonymous_cleanupeventcontainer_decision'
  ),
  # anonymous workflow page for creating an instance of object
  # for request type clean-up events (Müllsammelaktionen):
  # container (Container)
  path(
    'public/ce-request/container/create',
    view=CleanupEventContainerCreateAnonymousView.as_view(
      success_url=reverse_lazy('antragsmanagement:anonymous_index')
    ),
    name='anonymous_cleanupeventcontainer_create'
  )
]
