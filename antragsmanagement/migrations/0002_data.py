from django.db import migrations


def load_initial_data(apps, schema_editor):
  codelist_requeststatus = apps.get_model('antragsmanagement', 'CodelistRequestStatus')
  codelist_requeststatus.objects.create(
    ordinal=0,
    name='neu',
    icon='envelope'
  )
  codelist_requeststatus.objects.create(
    ordinal=1,
    name='in Bearbeitung',
    icon='gear'
  )
  codelist_requeststatus.objects.create(
    ordinal=2,
    name='abgeschlossen',
    icon='check'
  )
  codelist_requeststatus.objects.create(
    ordinal=3,
    name='zurückgewiesen',
    icon='thumbs-down'
  )


def reverse_func(apps, schema_editor):
  codelist_requeststatus = apps.get_model('antragsmanagement', 'CodelistRequestStatus')
  codelist_requeststatus.objects.all().delete()


class Migration(migrations.Migration):
  dependencies = [
    ('antragsmanagement', '0001_initial')
  ]

  operations = [
    migrations.RunPython(load_initial_data, reverse_func)
  ]
