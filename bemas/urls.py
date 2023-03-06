from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy
from rest_framework import routers

from bemas.models import Codelist
from .views.views import CodelistCreateView, CodelistDeleteView, CodelistIndexView, \
  CodelistsIndexView, CodelistUpdateView, IndexView

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
  if issubclass(model, Codelist):
    codelist_name = model.__name__
    codelist_name_lower = codelist_name.lower()

    # CodelistIndexView:
    # entry page for a codelist
    urlpatterns.append(
      path(
        'codelists/' + codelist_name_lower,
        view=login_required(CodelistIndexView.as_view(
          model=model
        )),
        name='codelists_' + codelist_name_lower
      )
    )

    # CodelistCreateView:
    # form page for creating a codelist
    urlpatterns.append(
      path(
        'codelists/' + codelist_name_lower + '/create',
        view=login_required(CodelistCreateView.as_view(
          model=model,
          success_url=reverse_lazy('bemas:' + 'codelists_' + codelist_name_lower)
        )),
        name='codelists_' + codelist_name_lower + '_create'
      )
    )

    # CodelistUpdateView:
    # form page for updating a codelist
    urlpatterns.append(
      path(
        'codelists/' + codelist_name_lower + '/update/<pk>',
        view=login_required(CodelistUpdateView.as_view(
          model=model,
          success_url=reverse_lazy('bemas:' + 'codelists_' + codelist_name_lower)
        )),
        name='codelists_' + codelist_name_lower + '_update'
      )
    )

    # CodelistDeleteView:
    # form page for deleting a codelist
    urlpatterns.append(
      path(
        'codelists/' + codelist_name_lower + '/delete/<pk>',
        view=login_required(CodelistDeleteView.as_view(
          model=model,
          success_url=reverse_lazy('bemas:' + 'codelists_' + codelist_name_lower)
        )),
        name='codelists_' + codelist_name_lower + '_delete'
      )
    )
