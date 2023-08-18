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
    title='Anlage an Wohnhaus',
    examples='Luftwärmepumpe, Fahrstuhl'
  )
  sector.objects.create(
    title='Anlage für gesundheitliche und soziale Zwecke',
    examples='Klinik, Kirche, Pflegeheim, Schule, Kindertagesstätte'
  )
  sector.objects.create(
    title='Baustelle/Einsatz von Geräten und Maschinen'
  )
  sector.objects.create(
    title='Einzelhandel',
    examples='Supermarkt, Bäckereifiliale'
  )
  sector.objects.create(
    title='Elektromagnetische Strahlung',
    examples='Erweiterung/Bau Antennenanlage, Hochspannungsleitung'
  )
  sector.objects.create(
    title='Fahrzeug- und Maschinenbau',
    examples='Bootsbau, Kfz-Bau, Werft'
  )
  sector.objects.create(
    title='Forschung/Universität'
  )
  sector.objects.create(
    title='Freizeitanlage',
    examples='Wasserski, Skaterpark, Spielplatz'
  )
  sector.objects.create(
    title='Gastgewerbe',
    examples='Schank-/Speisewirtschaft, Beherbergungsbetrieb, Diskothek'
  )
  sector.objects.create(
    title='Hafen/Umschlag/Liegeplatz'
  )
  sector.objects.create(
    title='Handel, Vermietung und Reparatur von Fahrzeugen, Maschinen und Anlagen',
    examples='Autohaus, Kfz-Werkstatt'
  )
  sector.objects.create(
    title='Kultureinrichtung',
    examples='Kino, Theater, Stadthalle'
  )
  sector.objects.create(
    title='landwirtschaftlicher Betrieb/Tierhaltung',
    examples='Tierheim, Tierpension'
  )
  sector.objects.create(
    title='produzierendes und verarbeitendes Gewerbe',
    examples='Bäckerei, Großküche, Holz-, Metall-, Kunststoffbearbeitung/-verarbeitung'
  )
  sector.objects.create(
    title='Stellplatzanlage/Parkhaus'
  )
  sector.objects.create(
    title='Speditionsbetrieb/Logistikunternehmen/Großhandel/Zusteller'
  )
  sector.objects.create(
    title='Sportanlage'
  )
  sector.objects.create(
    title='Tankstelle/Ladestation'
  )
  sector.objects.create(
    title='Veranstaltung im Freien',
    examples='Hanse Sail, Warnemünder Woche'
  )
  sector.objects.create(
    title='Verbrennungsanlage',
    examples='Heizung, Kamin, Heizkraftwerk, Krematorium'
  )
  sector.objects.create(
    title='Ver- und Entsorgung',
    examples='Deponie, Wasserwerk, Kläranlage'
  )
  sector.objects.create(
    title='Schienenverkehr',
    examples='Straßenbahnverkehr, Eisenbahnverkehr'
  )
  sector.objects.create(
    title='sonstige Anlage',
    examples='Windkraftanlage, Werbeanlage'
  )
  sector.objects.create(
    title='sonstige Dienstleistung und sonstiges Gewerbe',
    examples='chemische Reinigung, Nagelstudio, Fitnesscenter, Baubetrieb'
  )
  sector.objects.create(
    title='sonstiger Verkehr',
    examples='Schiffsverkehr, Luftverkehr'
  )
  sector.objects.create(
    title='Straßenverkehr'
  )
  type_of_event = apps.get_model('bemas', 'TypeOfEvent')
  type_of_event.objects.create(
    title='Besprechung',
    icon='comments'
  )
  type_of_event.objects.create(
    title='Ortsbegehung',
    icon='eye'
  )
  type_of_event.objects.create(
    title='Prognose/Messung',
    icon='gauge'
  )
  type_of_event.objects.create(
    title='Schriftverkehr',
    icon='envelope'
  )
  type_of_event.objects.create(
    title='Telefonat',
    icon='phone'
  )
  type_of_immission = apps.get_model('bemas', 'TypeOfImmission')
  type_of_immission.objects.create(
    title='Abgas/Rauch',
    icon='cloud'
  )
  type_of_immission.objects.create(
    title='Elektromagnetische Strahlung',
    icon='radiation'
  )
  type_of_immission.objects.create(
    title='Erschütterungen',
    icon='house-crack'
  )
  type_of_immission.objects.create(
    title='Geruch',
    icon='poop'
  )
  type_of_immission.objects.create(
    title='Lärm',
    icon='volume-high'
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
