from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy
from rest_framework import routers

from bemas.models import Codelist
from .views.base import GenericTableDataView
from .views.views_codelist import CodelistCreateView, CodelistDeleteView, CodelistTableView, \
  CodelistUpdateView
from .views.views_general import CodelistsIndexView, IndexView
from .views.views_objectclass import ContactDeleteView, GenericObjectclassCreateView, \
  GenericObjectclassTableView, GenericObjectclassUpdateView, OrganizationDeleteView, \
  OrganizationTableView, PersonDeleteView, ContactCreateView, ContactUpdateView

router = routers.DefaultRouter()

api_urlpatterns = router.urls

app_name = 'bemas'


#
# general views
#

urlpatterns = [
  # main page
  path(
    '',
    view=login_required(IndexView.as_view()),
    name='index'
  ),
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

    # table data composition for a codelist
    urlpatterns.append(
      path(
        'codelists/' + codelist_name_lower + '/tabledata',
        view=login_required(GenericTableDataView.as_view(
          model=model
        )),
        name='codelists_' + codelist_name_lower + '_tabledata'
      )
    )

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

    # form page for creating a codelist instance
    urlpatterns.append(
      path(
        'codelists/' + codelist_name_lower + '/create',
        view=login_required(CodelistCreateView.as_view(
          model=model,
          success_url=reverse_lazy('bemas:' + 'codelists_' + codelist_name_lower + '_table')
        )),
        name='codelists_' + codelist_name_lower + '_create'
      )
    )

    # form page for updating a codelist instance
    urlpatterns.append(
      path(
        'codelists/' + codelist_name_lower + '/update/<pk>',
        view=login_required(CodelistUpdateView.as_view(
          model=model,
          success_url=reverse_lazy('bemas:' + 'codelists_' + codelist_name_lower + '_table')
        )),
        name='codelists_' + codelist_name_lower + '_update'
      )
    )

    # form page for deleting a codelist instance
    urlpatterns.append(
      path(
        'codelists/' + codelist_name_lower + '/delete/<pk>',
        view=login_required(CodelistDeleteView.as_view(
          model=model,
          success_url=reverse_lazy('bemas:' + 'codelists_' + codelist_name_lower + '_table')
        )),
        name='codelists_' + codelist_name_lower + '_delete'
      )
    )

  #
  # views for object class organization
  #
  elif model.__name__ == 'Organization':

    # table data composition for object class organization
    urlpatterns.append(
      path(
        'organization/tabledata',
        view=login_required(GenericTableDataView.as_view(
          model=model
        )),
        name='organization_tabledata'
      )
    )

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

    # form page for creating an instance of object class organization
    urlpatterns.append(
      path(
        'organization/create',
        view=login_required(GenericObjectclassCreateView.as_view(
          model=model,
          success_url=reverse_lazy('bemas:organization_table')
        )),
        name='organization_create'
      )
    )

    # form page for updating an instance of object class organization
    urlpatterns.append(
      path(
        'organization/update/<pk>',
        view=login_required(GenericObjectclassUpdateView.as_view(
          model=model,
          success_url=reverse_lazy('bemas:organization_table')
        )),
        name='organization_update'
      )
    )

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

    # table data composition for object class person
    urlpatterns.append(
      path(
        'person/tabledata',
        view=login_required(GenericTableDataView.as_view(
          model=model
        )),
        name='person_tabledata'
      )
    )

    # table page for object class person
    urlpatterns.append(
      path(
        'person/table',
        view=login_required(GenericObjectclassTableView.as_view(
          model=model
        )),
        name='person_table'
      )
    )

    # form page for creating an instance of object class person
    urlpatterns.append(
      path(
        'person/create',
        view=login_required(GenericObjectclassCreateView.as_view(
          model=model,
          success_url=reverse_lazy('bemas:person_table')
        )),
        name='person_create'
      )
    )

    # form page for updating an instance of object class person
    urlpatterns.append(
      path(
        'person/update/<pk>',
        view=login_required(GenericObjectclassUpdateView.as_view(
          model=model,
          success_url=reverse_lazy('bemas:person_table')
        )),
        name='person_update'
      )
    )

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

  #
  # views for object class contact
  #
  elif model.__name__ == 'Contact':

    # form page for creating an instance of object class contact
    urlpatterns.append(
      path(
        'contact/create',
        view=login_required(ContactCreateView.as_view(
          model=model,
          success_url=reverse_lazy('bemas:organization_table')
        )),
        name='contact_create'
      )
    )

    # form page for updating an instance of object class contact
    urlpatterns.append(
      path(
        'contact/update/<pk>',
        view=login_required(ContactUpdateView.as_view(
          model=model,
          success_url=reverse_lazy('bemas:organization_table')
        )),
        name='contact_update'
      )
    )

    # form page for deleting an instance of object class contact
    urlpatterns.append(
      path(
        'contact/delete/<pk>',
        view=login_required(ContactDeleteView.as_view(
          model=model,
          success_url=reverse_lazy('bemas:organization_table')
        )),
        name='contact_delete'
      )
    )
