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
  cleanupevent_codelist_wastequantity = apps.get_model('antragsmanagement', 'CleanupEventCodelistWasteQuantity')
  cleanupevent_codelist_wastequantity.objects.create(
    ordinal=0,
    name='weniger als 3 m³'
  )
  cleanupevent_codelist_wastequantity.objects.create(
    ordinal=1,
    name='zwischen 3 und 5 m³'
  )
  cleanupevent_codelist_wastequantity.objects.create(
    ordinal=2,
    name='zwischen 5 und 10 m³'
  )
  cleanupevent_codelist_wastequantity.objects.create(
    ordinal=3,
    name='mehr als 10 m³'
  )
  cleanupevent_codelist_wastetype = apps.get_model('antragsmanagement', 'CleanupEventCodelistWasteType')
  cleanupevent_codelist_wastetype.objects.create(
    name='Hausmüll'
  )
  cleanupevent_codelist_wastetype.objects.create(
    name='Metall/Schrott'
  )
  cleanupevent_codelist_wastetype.objects.create(
    name='Reifen'
  )
  cleanupevent_codelist_wastetype.objects.create(
    name='Sondermüll (Öl, Lack, Farben)'
  )
  cleanupevent_codelist_wastetype.objects.create(
    name='Sperrmüll'
  )
  cleanupevent_codelist_wastetype.objects.create(
    name='Verpackungen/Plastik'
  )
  cleanupevent_codelist_equipment = apps.get_model('antragsmanagement', 'CleanupEventCodelistEquipment')
  cleanupevent_codelist_equipment.objects.create(
    name='Behälter'
  )
  cleanupevent_codelist_equipment.objects.create(
    name='Eimer'
  )
  cleanupevent_codelist_equipment.objects.create(
    name='Handschuhe'
  )
  cleanupevent_codelist_equipment.objects.create(
    name='Müllbeutel'
  )
  cleanupevent_codelist_equipment.objects.create(
    name='Zangen'
  )


def reverse_func(apps, schema_editor):
  cleanupevent_codelist_equipment = apps.get_model('antragsmanagement', 'CleanupEventCodelistEquipment')
  cleanupevent_codelist_equipment.objects.all().delete()
  cleanupevent_codelist_wastetype = apps.get_model('antragsmanagement', 'CleanupEventCodelistWasteType')
  cleanupevent_codelist_wastetype.objects.all().delete()
  cleanupevent_codelist_wastequantity = apps.get_model('antragsmanagement', 'CleanupEventCodelistWasteQuantity')
  cleanupevent_codelist_wastequantity.objects.all().delete()
  codelist_requeststatus = apps.get_model('antragsmanagement', 'CodelistRequestStatus')
  codelist_requeststatus.objects.all().delete()


class Migration(migrations.Migration):
  dependencies = [
    ('antragsmanagement', '0001_initial')
  ]

  operations = [
    migrations.RunPython(load_initial_data, reverse_func)
  ]
