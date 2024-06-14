from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy
from rest_framework import routers

from .views.views import IndexView, AuthorityUpdateView, EmailUpdateView, RequesterCreateView

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
      success_url=reverse_lazy(app_name + ':' + 'index')
    )),
    name='authority_update'
  ),
  # form page for updating an instance of general object:
  # email (E-Mail)
  path(
    'email/update/<pk>',
    view=login_required(EmailUpdateView.as_view(
      success_url=reverse_lazy(app_name + ':' + 'index')
    )),
    name='email_update'
  ),
  # form page for creating an instance of general object:
  # requester (Antragsteller:in)
  path(
    'requester/create',
    view=login_required(RequesterCreateView.as_view(
      success_url=reverse_lazy(app_name + ':' + 'index')
    )),
    name='requester_create'
  )
]
