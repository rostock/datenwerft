from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.urls import path
from rest_framework import routers

from .views.views import CodelistIndexView, CodelistsIndexView, IndexView

router = routers.DefaultRouter()

api_urlpatterns = router.urls

app_name = 'bemas'


#
# general views
#

urlpatterns = [
  # IndexView:
  # main page
  path(
    '',
    view=login_required(IndexView.as_view()),
    name='index'
  ),
  # CodelistsIndexView:
  # codelists entry page
  path(
    'codelists',
    view=login_required(CodelistsIndexView.as_view()),
    name='codelists'
  )
]

#
# codelist views
#

models = apps.get_app_config(app_name).get_models()
for model in models:
  if hasattr(model._meta, 'codelist') and model._meta.codelist is True:
    codelist_name = model.__name__
    codelist_name_lower = codelist_name.lower()

    # CodelistIndexView:
    # entry page for a codelist
    urlpatterns.append(
      path(
        'codelists/' + codelist_name_lower,
        view=login_required(CodelistIndexView.as_view(codelist=model)),
        name='codelists_' + codelist_name_lower
      )
    )
