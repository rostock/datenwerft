from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy
from rest_framework import routers

from .views.views import IndexView, AuthorityUpdateView, EmailUpdateView, RequesterCreateView, \
  RequesterUpdateView, CleanupEventRequestCreateView, CleanupEventRequestUpdateView, \
  CleanupEventEventCreateView

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
  # form page for updating an instance of general object:
  # authority (Behörde)
  path(
    'authority/update/<pk>',
    view=login_required(AuthorityUpdateView.as_view(
      success_url=reverse_lazy('antragsmanagement:index')
    )),
    name='authority_update'
  ),
  # form page for updating an instance of general object:
  # email (E-Mail)
  path(
    'email/update/<pk>',
    view=login_required(EmailUpdateView.as_view(
      success_url=reverse_lazy('antragsmanagement:index')
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
    view=login_required(CleanupEventRequestUpdateView.as_view(
      success_url=reverse_lazy('antragsmanagement:index')
    )),
    name='cleanupeventrequest_update'
  ),
  # form page for creating an instance of object for request type clean-up events
  # (Müllsammelaktionen):
  # event (Aktion)
  path(
    'cleanupeventevent/create',
    view=login_required(CleanupEventEventCreateView.as_view(
      success_url=reverse_lazy('antragsmanagement:index')
    )),
    name='cleanupeventevent_create'
  )
]
