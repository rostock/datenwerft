from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy
from rest_framework import routers

from bemas.models import Codelist
from .views.views_codelist import CodelistCreateView, CodelistDeleteView, CodelistIndexView, \
  CodelistTableDataView, CodelistTableView, CodelistUpdateView
from .views.views_general import CodelistsIndexView, IndexView
from .views.views_objectclass import OrganizationCreateView, OrganizationUpdateView, \
  OrganizationDeleteView, OrganizationTableDataView, OrganizationTableView, PersonCreateView, \
  PersonUpdateView, PersonDeleteView, PersonTableDataView, PersonTableView

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

models = apps.get_app_config(app_name).get_models()
for model in models:

  #
  # codelist views
  #
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

    # CodelistTableDataView:
    # table data composition for a codelist
    urlpatterns.append(
      path(
        'codelists/' + codelist_name_lower + '/tabledata',
        view=login_required(CodelistTableDataView.as_view(
          model=model
        )),
        name='codelists_' + codelist_name_lower + '_tabledata'
      )
    )

    # CodelistTableView:
    # table page for a codelist
    urlpatterns.append(
      path(
        'codelists/' + codelist_name_lower + '/table',
        view=login_required(CodelistTableView.as_view(
          model=model
        )),
        name='codelists_' + codelist_name_lower + '_table'
      )
    )

    # CodelistCreateView:
    # form page for creating a codelist instance
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
    # form page for updating a codelist instance
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
    # form page for deleting a codelist instance
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

  #
  # views for object class organization
  #
  elif model.__name__ == 'Organization':

    # OrganizationTableDataView:
    # table data composition for object class organization
    urlpatterns.append(
      path(
        'organization/tabledata',
        view=login_required(OrganizationTableDataView.as_view(
          model=model
        )),
        name='organization_tabledata'
      )
    )

    # OrganizationTableView:
    # table page for object class organization
    urlpatterns.append(
      path(
        'organization/table',
        view=login_required(OrganizationTableView.as_view(
          model=model
        )),
        name='organization_table'
      )
    )

    # OrganizationCreateView:
    # form page for creating an instance of object class organization
    urlpatterns.append(
      path(
        'organization/create',
        view=login_required(OrganizationCreateView.as_view(
          model=model,
          success_url=reverse_lazy('bemas:organization_table')
        )),
        name='organization_create'
      )
    )

    # OrganizationUpdateView:
    # form page for updating an instance of object class organization
    urlpatterns.append(
      path(
        'organization/update/<pk>',
        view=login_required(OrganizationUpdateView.as_view(
          model=model,
          success_url=reverse_lazy('bemas:organization_table')
        )),
        name='organization_update'
      )
    )

    # OrganizationDeleteView:
    # form page for deleting an instance of object class organization
    urlpatterns.append(
      path(
        'organization/delete/<pk>',
        view=login_required(OrganizationDeleteView.as_view(
          model=model,
          success_url=reverse_lazy('bemas:organization_table')
        )),
        name='organization_delete'
      )
    )

  #
  # views for object class person
  #
  elif model.__name__ == 'Person':

    # PersonTableDataView:
    # table data composition for object class person
    urlpatterns.append(
      path(
        'person/tabledata',
        view=login_required(PersonTableDataView.as_view(
          model=model
        )),
        name='person_tabledata'
      )
    )

    # PersonTableView:
    # table page for object class person
    urlpatterns.append(
      path(
        'person/table',
        view=login_required(PersonTableView.as_view(
          model=model
        )),
        name='person_table'
      )
    )

    # PersonCreateView:
    # form page for creating an instance of object class person
    urlpatterns.append(
      path(
        'person/create',
        view=login_required(PersonCreateView.as_view(
          model=model,
          success_url=reverse_lazy('bemas:person_table')
        )),
        name='person_create'
      )
    )

    # PersonUpdateView:
    # form page for updating an instance of object class person
    urlpatterns.append(
      path(
        'person/update/<pk>',
        view=login_required(PersonUpdateView.as_view(
          model=model,
          success_url=reverse_lazy('bemas:person_table')
        )),
        name='person_update'
      )
    )

    # PersonDeleteView:
    # form page for deleting an instance of object class person
    urlpatterns.append(
      path(
        'person/delete/<pk>',
        view=login_required(PersonDeleteView.as_view(
          model=model,
          success_url=reverse_lazy('bemas:person_table')
        )),
        name='person_delete'
      )
    )
