from django.db import migrations


def load_initial_data(apps, schema_editor):
  status = apps.get_model('bemas', 'Status')
  status.objects.create(
    ordinal=1,
    title='in Bearbeitung',
    icon='gear'
  )
  status.objects.create(
    ordinal=2,
    title='abgeschlossen',
    icon='check'
  )
  sector = apps.get_model('bemas', 'Sector')
  sector.objects.create(
    title='Baubetrieb'
  )
  type_of_event = apps.get_model('bemas', 'TypeOfEvent')
  type_of_event.objects.create(
    title='Briefpost',
    icon='envelope'
  )
  type_of_event.objects.create(
    title='E-Mail',
    icon='at'
  )
  type_of_event.objects.create(
    title='Meeting',
    icon='handshake-simple'
  )
  type_of_event.objects.create(
    title='Messung',
    icon='gauge'
  )
  type_of_event.objects.create(
    title='Telefonat',
    icon='phone'
  )
  type_of_event.objects.create(
    title='Vor-Ort-Begehung',
    icon='eye'
  )
  type_of_immission = apps.get_model('bemas', 'TypeOfImmission')
  type_of_immission.objects.create(
    title='Elektromagnetik',
    icon='radiation'
  )
  type_of_immission.objects.create(
    title='Erschütterung',
    icon='house-crack'
  )
  type_of_immission.objects.create(
    title='Geräusche',
    icon='volume-high'
  )
  type_of_immission.objects.create(
    title='Geruch',
    icon='poop'
  )
  type_of_immission.objects.create(
    title='Licht',
    icon='lightbulb'
  )
  type_of_immission.objects.create(
    title='Staub',
    icon='smog'
  )


def reverse_func(apps, schema_editor):
  status = apps.get_model('bemas', 'Status')
  status.objects.all().delete()
  sector = apps.get_model('bemas', 'Sector')
  sector.objects.all().delete()
  type_of_event = apps.get_model('bemas', 'TypeOfEvent')
  type_of_event.objects.all().delete()
  type_of_immission = apps.get_model('bemas', 'TypeOfImmission')
  type_of_immission.objects.all().delete()


class Migration(migrations.Migration):
  dependencies = [
    ('bemas', '0001_initial')
  ]

  operations = [
    migrations.RunPython(load_initial_data, reverse_func)
  ]
