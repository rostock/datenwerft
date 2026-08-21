from django.db import migrations

OLD_CHILDREN_SLUG = 'childrenandyouthservice'
OLD_FAMILY_SLUG = 'familyservice'
NEW_SLUG = 'childrenyouthandfamilyservice'

M2M_FIELDS = ['topic', 'target_group', 'legal_basis']

# Felder, die beim Kopieren gesondert behandelt werden:
# - id: wird neu vergeben
# - published_version: Selbstreferenz, erst im zweiten Durchlauf auflösbar
# - created_at/updated_at: auto_now_add/auto_now, werden per .update() nachgezogen
SKIP_FIELDS = {'id', 'published_version', 'created_at', 'updated_at'}


def merge_family_services(apps, schema_editor):
  """
  Überführt alle Angebote für Familien in das zusammengeführte Modell
  ChildrenYouthAndFamilyService und zieht sämtliche Verweise nach, die den
  Modellnamen als String führen (service_type/service_id).
  """
  db = schema_editor.connection.alias

  FamilyService = apps.get_model('angebotsdb', 'FamilyService')
  Target = apps.get_model('angebotsdb', 'ChildrenYouthAndFamilyService')
  ServiceImage = apps.get_model('angebotsdb', 'ServiceImage')
  ReviewTask = apps.get_model('angebotsdb', 'ReviewTask')
  OrgUnitServicePermission = apps.get_model('angebotsdb', 'OrgUnitServicePermission')

  copy_fields = [
    field.attname
    for field in FamilyService._meta.concrete_fields
    if field.name not in SKIP_FIELDS
  ]

  # ------------------------------------------------------------------
  # 1./2. Zeilen kopieren (zunächst ohne Selbstreferenz), Zeitstempel bewahren
  # ------------------------------------------------------------------
  pk_map = {}
  old_services = list(FamilyService.objects.using(db).order_by('pk'))
  for old in old_services:
    new = Target(**{name: getattr(old, name) for name in copy_fields})
    new.published_version_id = None
    new.save(using=db)
    pk_map[old.pk] = new.pk
    # created_at (auto_now_add) und updated_at (auto_now) wurden beim Insert
    # überschrieben; .update() umgeht die automatische Zeitstempel-Logik
    Target.objects.using(db).filter(pk=new.pk).update(
      created_at=old.created_at,
      updated_at=old.updated_at,
    )

  # ------------------------------------------------------------------
  # 3. Selbstreferenzen der Draft-Copies auflösen
  # ------------------------------------------------------------------
  for old in old_services:
    if old.published_version_id is None:
      continue
    new_target_pk = pk_map.get(old.published_version_id)
    if new_target_pk is None:
      continue
    Target.objects.using(db).filter(pk=pk_map[old.pk]).update(
      published_version_id=new_target_pk
    )

  # ------------------------------------------------------------------
  # 4. M2M-Beziehungen übertragen
  # ------------------------------------------------------------------
  for old in old_services:
    new = Target.objects.using(db).get(pk=pk_map[old.pk])
    for m2m in M2M_FIELDS:
      related_ids = list(getattr(old, m2m).using(db).values_list('pk', flat=True))
      if related_ids:
        getattr(new, m2m).set(related_ids)

  # ------------------------------------------------------------------
  # 5./6. ServiceImage und ReviewTask umhängen
  # ------------------------------------------------------------------
  for model in (ServiceImage, ReviewTask):
    for row in model.objects.using(db).filter(service_type=OLD_FAMILY_SLUG):
      new_service_id = pk_map.get(row.service_id)
      if new_service_id is None:
        # verwaister Verweis auf ein nicht mehr existierendes Familienangebot:
        # nicht umschreiben, sonst zeigte er nach dem Merge auf einen fremden
        # Datensatz mit zufällig gleicher ID
        row.delete()
        continue
      row.service_type = NEW_SLUG
      row.service_id = new_service_id
      row.save(using=db)

  # ------------------------------------------------------------------
  # 7. Alt-Slug der Kinder-/Jugendangebote nachziehen
  #    (service_id bleibt gültig, da RenameModel die PKs erhalten hat)
  # ------------------------------------------------------------------
  for model in (ServiceImage, ReviewTask):
    model.objects.using(db).filter(service_type=OLD_CHILDREN_SLUG).update(
      service_type=NEW_SLUG
    )

  # ------------------------------------------------------------------
  # 8. OE-Angebot-Berechtigungen zusammenführen (unique_together beachten)
  # ------------------------------------------------------------------
  already_merged = set(
    OrgUnitServicePermission.objects.using(db)
    .filter(service_type=NEW_SLUG)
    .values_list('organisational_unit_id', flat=True)
  )
  permissions = OrgUnitServicePermission.objects.using(db).filter(
    service_type__in=[OLD_CHILDREN_SLUG, OLD_FAMILY_SLUG]
  )
  for permission in permissions.order_by('organisational_unit_id', 'pk'):
    if permission.organisational_unit_id in already_merged:
      permission.delete()
      continue
    already_merged.add(permission.organisational_unit_id)
    permission.service_type = NEW_SLUG
    permission.save(using=db)


class Migration(migrations.Migration):
  dependencies = [
    (
      'angebotsdb',
      '0007_rename_childrenandyouthservice_childrenyouthandfamilyservice_and_more',
    ),
  ]

  operations = [
    # Nicht verlustfrei umkehrbar: die Herkunft der Datensätze geht durch die
    # Zusammenführung verloren. Rückweg ist der Datenbank-Dump vor der Migration.
    migrations.RunPython(merge_family_services, migrations.RunPython.noop),
  ]
