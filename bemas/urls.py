from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy
from rest_framework import routers

from bemas.models import Codelist
from .views.base import GenericTableDataView, GenericMapDataView
from .views.views_codelist import CodelistCreateView, CodelistDeleteView, CodelistTableView, \
  CodelistUpdateView
from .views.views_general import CodelistsIndexView, IndexView, MapView, OrphanedDataView
from .views.views_objectclass import ComplaintDeleteView, GenericObjectclassCreateView, \
  GenericObjectclassDeleteView, GenericObjectclassTableView, GenericObjectclassUpdateView, \
  OrganizationDeleteView, PersonDeleteView

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
  ),
  # map page
  path(
    'map',
    view=login_required(MapView.as_view()),
    name='map'
  ),
  # map page:
  # filter by model and subset
  path(
    'map/<model>/<subset_pk>',
    view=login_required(MapView.as_view()),
    name='map_model_subset'
  ),
  # orphaned data page
  path(
    'orphaned-data',
    view=login_required(OrphanedDataView.as_view()),
    name='orphaned_data'
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
        view=login_required(GenericObjectclassTableView.as_view(
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
          model=model
        )),
        name='organization_create'
      )
    )

    # form page for updating an instance of object class organization
    urlpatterns.append(
      path(
        'organization/update/<pk>',
        view=login_required(GenericObjectclassUpdateView.as_view(
          model=model
        )),
        name='organization_update'
      )
    )

    # form page for deleting an instance of object class organization
    urlpatterns.append(
      path(
        'organization/delete/<pk>',
        view=login_required(OrganizationDeleteView.as_view(
          model=model
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
          model=model
        )),
        name='person_create'
      )
    )

    # form page for updating an instance of object class person
    urlpatterns.append(
      path(
        'person/update/<pk>',
        view=login_required(GenericObjectclassUpdateView.as_view(
          model=model
        )),
        name='person_update'
      )
    )

    # form page for deleting an instance of object class person
    urlpatterns.append(
      path(
        'person/delete/<pk>',
        view=login_required(PersonDeleteView.as_view(
          model=model
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
        view=login_required(GenericObjectclassCreateView.as_view(
          model=model
        )),
        name='contact_create'
      )
    )

    # form page for updating an instance of object class contact
    urlpatterns.append(
      path(
        'contact/update/<pk>',
        view=login_required(GenericObjectclassUpdateView.as_view(
          model=model
        )),
        name='contact_update'
      )
    )

    # form page for deleting an instance of object class contact
    urlpatterns.append(
      path(
        'contact/delete/<pk>',
        view=login_required(GenericObjectclassDeleteView.as_view(
          model=model
        )),
        name='contact_delete'
      )
    )

  #
  # views for object class originator
  #
  elif model.__name__ == 'Originator':

    # table data composition for object class originator
    urlpatterns.append(
      path(
        'originator/tabledata',
        view=login_required(GenericTableDataView.as_view(
          model=model
        )),
        name='originator_tabledata'
      )
    )

    # table data composition for object class originator:
    # filter by subset
    urlpatterns.append(
      path(
        'originator/tabledata/<subset_pk>',
        view=login_required(GenericTableDataView.as_view(
          model=model
        )),
        name='originator_tabledata_subset'
      )
    )

    # table page for object class originator
    urlpatterns.append(
      path(
        'originator/table',
        view=login_required(GenericObjectclassTableView.as_view(
          model=model
        )),
        name='originator_table'
      )
    )

    # table page for object class originator:
    # filter by subset
    urlpatterns.append(
      path(
        'originator/table/<subset_pk>',
        view=login_required(GenericObjectclassTableView.as_view(
          model=model
        )),
        name='originator_table_subset'
      )
    )

    # form page for creating an instance of object class originator
    urlpatterns.append(
      path(
        'originator/create',
        view=login_required(GenericObjectclassCreateView.as_view(
          model=model
        )),
        name='originator_create'
      )
    )

    # form page for updating an instance of object class originator
    urlpatterns.append(
      path(
        'originator/update/<pk>',
        view=login_required(GenericObjectclassUpdateView.as_view(
          model=model
        )),
        name='originator_update'
      )
    )

    # form page for deleting an instance of object class originator
    urlpatterns.append(
      path(
        'originator/delete/<pk>',
        view=login_required(GenericObjectclassDeleteView.as_view(
          model=model
        )),
        name='originator_delete'
      )
    )

    # map data composition for object class originator
    urlpatterns.append(
      path(
        'originator/mapdata',
        view=login_required(GenericMapDataView.as_view(
          model=model
        )),
        name='originator_mapdata'
      )
    )

    # map data composition for object class originator:
    # filter by subset
    urlpatterns.append(
      path(
        'originator/mapdata/<subset_pk>',
        view=login_required(GenericMapDataView.as_view(
          model=model
        )),
        name='originator_mapdata_subset'
      )
    )

  #
  # views for object class complaint
  #
  elif model.__name__ == 'Complaint':

    # table data composition for object class complaint
    urlpatterns.append(
      path(
        'complaint/tabledata',
        view=login_required(GenericTableDataView.as_view(
          model=model
        )),
        name='complaint_tabledata'
      )
    )

    # table data composition for object class complaint:
    # filter by subset
    urlpatterns.append(
      path(
        'complaint/tabledata/<subset_pk>',
        view=login_required(GenericTableDataView.as_view(
          model=model
        )),
        name='complaint_tabledata_subset'
      )
    )

    # table page for object class complaint
    urlpatterns.append(
      path(
        'complaint/table',
        view=login_required(GenericObjectclassTableView.as_view(
          model=model
        )),
        name='complaint_table'
      )
    )

    # table page for object class complaint:
    # filter by subset
    urlpatterns.append(
      path(
        'complaint/table/<subset_pk>',
        view=login_required(GenericObjectclassTableView.as_view(
          model=model
        )),
        name='complaint_table_subset'
      )
    )

    # form page for creating an instance of object class complaint
    urlpatterns.append(
      path(
        'complaint/create',
        view=login_required(GenericObjectclassCreateView.as_view(
          model=model
        )),
        name='complaint_create'
      )
    )

    # form page for updating an instance of object class complaint
    urlpatterns.append(
      path(
        'complaint/update/<pk>',
        view=login_required(GenericObjectclassUpdateView.as_view(
          model=model
        )),
        name='complaint_update'
      )
    )

    # form page for deleting an instance of object class complaint
    urlpatterns.append(
      path(
        'complaint/delete/<pk>',
        view=login_required(ComplaintDeleteView.as_view(
          model=model
        )),
        name='complaint_delete'
      )
    )

    # map data composition for object class complaint
    urlpatterns.append(
      path(
        'complaint/mapdata',
        view=login_required(GenericMapDataView.as_view(
          model=model
        )),
        name='complaint_mapdata'
      )
    )

    # map data composition for object class complaint:
    # filter by subset
    urlpatterns.append(
      path(
        'complaint/mapdata/<subset_pk>',
        view=login_required(GenericMapDataView.as_view(
          model=model
        )),
        name='complaint_mapdata_subset'
      )
    )

  #
  # views for object class log entry
  #
  elif model.__name__ == 'LogEntry':

    # table data composition for object class log entry
    urlpatterns.append(
      path(
        'logentry/tabledata',
        view=login_required(GenericTableDataView.as_view(
          model=model
        )),
        name='logentry_tabledata'
      )
    )

    # table data composition for object class log entry:
    # filter by model
    urlpatterns.append(
      path(
        'logentry/tabledata/<model>',
        view=login_required(GenericTableDataView.as_view(
          model=model
        )),
        name='logentry_tabledata_model'
      )
    )

    # table data composition for object class log entry:
    # filter by model and object
    urlpatterns.append(
      path(
        'logentry/tabledata/<model>/<object_pk>',
        view=login_required(GenericTableDataView.as_view(
          model=model
        )),
        name='logentry_tabledata_model_object'
      )
    )

    # table page for object class log entry
    urlpatterns.append(
      path(
        'logentry/table',
        view=login_required(GenericObjectclassTableView.as_view(
          model=model
        )),
        name='logentry_table'
      )
    )

    # table page for object class log entry:
    # filter by model
    urlpatterns.append(
      path(
        'logentry/table/<model>',
        view=login_required(GenericObjectclassTableView.as_view(
          model=model
        )),
        name='logentry_table_model'
      )
    )

    # table page for object class log entry:
    # filter by model and object
    urlpatterns.append(
      path(
        'logentry/table/<model>/<object_pk>',
        view=login_required(GenericObjectclassTableView.as_view(
          model=model
        )),
        name='logentry_table_model_object'
      )
    )

  #
  # views for object class event
  #
  elif model.__name__ == 'Event':

    # table data composition for object class event
    urlpatterns.append(
      path(
        'event/tabledata',
        view=login_required(GenericTableDataView.as_view(
          model=model
        )),
        name='event_tabledata'
      )
    )

    # table data composition for object class event:
    # filter by complaint
    urlpatterns.append(
      path(
        'event/tabledata/<complaint_pk>',
        view=login_required(GenericTableDataView.as_view(
          model=model
        )),
        name='event_tabledata_complaint'
      )
    )

    # table page for object class event
    urlpatterns.append(
      path(
        'event/table',
        view=login_required(GenericObjectclassTableView.as_view(
          model=model
        )),
        name='event_table'
      )
    )

    # table page for object class event:
    # filter by complaint
    urlpatterns.append(
      path(
        'event/table/<complaint_pk>',
        view=login_required(GenericObjectclassTableView.as_view(
          model=model
        )),
        name='event_table_complaint'
      )
    )

    # form page for creating an instance of object class event
    urlpatterns.append(
      path(
        'event/create',
        view=login_required(GenericObjectclassCreateView.as_view(
          model=model
        )),
        name='event_create'
      )
    )

    # form page for updating an instance of object class event
    urlpatterns.append(
      path(
        'event/update/<pk>',
        view=login_required(GenericObjectclassUpdateView.as_view(
          model=model
        )),
        name='event_update'
      )
    )

    # form page for deleting an instance of object class event
    urlpatterns.append(
      path(
        'event/delete/<pk>',
        view=login_required(GenericObjectclassDeleteView.as_view(
          model=model
        )),
        name='event_delete'
      )
    )
