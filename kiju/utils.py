from .constants_vars import ADMIN_GROUP, USERS_GROUP

# ---------------------------------------------------------------------------
# Phase 2 – Snapshot, Diff & Inbox-Hilfsfunktionen
# ---------------------------------------------------------------------------


def create_service_snapshot(service) -> dict:
  """
  Erzeugt ein JSON-serialisierbares Dict aller Feldwerte eines Service.

  - Einfache Felder werden direkt übernommen.
  - ForeignKey-Felder werden als {'id': pk, 'display': str(obj)} gespeichert.
  - ManyToMany-Felder werden als Liste von {'id': pk, 'display': str(obj)} gespeichert.
  - Geometrie-Felder werden als WKT-String gespeichert.
  - Datetime/Date/Time-Felder werden als ISO-8601-String gespeichert.

  :param service: Service-Instanz
  :return: JSON-serialisierbares Dict
  """
  snapshot = {}

  # Konkrete (Datenbank-)Felder
  for field in service._meta.concrete_fields:
    value = getattr(service, field.name)

    if value is None:
      snapshot[field.name] = None
    elif hasattr(value, 'wkt'):
      # GeometryField → WKT-Repräsentation
      snapshot[field.name] = value.wkt
    elif hasattr(value, 'isoformat'):
      # DateTime / Date / Time
      snapshot[field.name] = value.isoformat()
    elif hasattr(value, 'name') and hasattr(value, 'storage'):
      # FileField / ImageField → Dateipfad als String oder None
      snapshot[field.name] = value.name if value.name else None
    elif hasattr(value, 'pk') and hasattr(value, '__str__'):
      # ForeignKey-Objekt
      snapshot[field.name] = {'id': value.pk, 'display': str(value)}
    elif isinstance(value, (list, dict)):
      # JSONField — bereits JSON-serialisierbar, direkt übernehmen
      snapshot[field.name] = value
    elif isinstance(value, (str, int, float, bool)):
      # Skalare Basistypen direkt übernehmen
      snapshot[field.name] = value
    else:
      # Fallback: in String konvertieren, damit JSON-Serialisierung nicht bricht
      snapshot[field.name] = str(value)

  # ManyToMany-Felder
  for field in service._meta.many_to_many:
    related_objects = getattr(service, field.name).all()
    snapshot[field.name] = [{'id': obj.pk, 'display': str(obj)} for obj in related_objects]

  # ServiceImage-Informationen im Snapshot erfassen
  from .models.services import ServiceImage

  service_type = service.__class__.__name__.lower()
  images = ServiceImage.objects.filter(service_type=service_type, service_id=service.pk)
  snapshot['_images'] = [
    {'id': img.pk, 'image': img.image.name, 'position': img.position} for img in images
  ]

  return snapshot


def compute_diff(old_snapshot: dict, new_snapshot: dict) -> dict:
  """
  Vergleicht zwei Service-Snapshots und gibt ein Dict der geänderten Felder zurück.

  Rückgabeformat:
    {
      'field_name': {'old': <alter Wert>, 'new': <neuer Wert>},
      ...
    }

  Nur Felder, die sich tatsächlich geändert haben, erscheinen im Ergebnis.
  Felder, die nur in einem der beiden Snapshots existieren, werden ebenfalls
  als Änderung gewertet (None als Platzhalter für den fehlenden Wert).

  :param old_snapshot: Snapshot des letzten freigegebenen Zustands
  :param new_snapshot: Snapshot der aktuellen Einreichung
  :return: Dict der geänderten Felder
  """
  diff = {}
  all_keys = set(list(old_snapshot.keys()) + list(new_snapshot.keys()))

  for key in all_keys:
    old_val = old_snapshot.get(key)
    new_val = new_snapshot.get(key)
    if old_val != new_val:
      diff[key] = {'old': old_val, 'new': new_val}

  return diff


def get_service_instance(service_type: str, service_id: int):
  """
  Löst service_type (lowercase Modellname) + service_id zu einer konkreten
  Service-Instanz auf. Gibt None zurück wenn das Modell nicht gefunden wird
  oder das Objekt nicht existiert.

  :param service_type: lowercase Modellname, z.B. 'childrenandyouthservice'
  :param service_id: Primärschlüssel des Service-Objekts
  :return: Service-Instanz oder None
  """
  from django.apps import apps

  try:
    model = apps.get_model('kiju', service_type)
    return model.objects.get(pk=service_id)
  except Exception:
    return None


def get_inbox_messages(user):
  """
  Liefert alle unerledigten InboxMessages für den übergebenen User.

  Die Zuordnung erfolgt über das UserProfile:
  - Hat der User eine OrgUnit → Reviewer-Aufgaben (review_request)
  - Hat der User einen Provider → Überarbeitungs-Aufgaben (revision_request)
  - Admins und Superuser sehen alle unerledigten Nachrichten.

  Die Nachrichten werden nach Erstellungsdatum absteigend sortiert zurückgegeben.

  :param user: Django-User-Instanz
  :return: QuerySet von InboxMessage-Objekten
  """
  from django.db.models import Q

  from .models.base import InboxMessage

  if user.is_superuser or is_angebotsdb_admin(user):
    return InboxMessage.objects.filter(is_resolved=False).order_by('-created_at')

  org_unit = get_user_org_unit(user)
  provider = get_user_provider(user)

  if not org_unit and not provider:
    return InboxMessage.objects.none()

  query = Q()
  if org_unit:
    query |= Q(target_org_unit=org_unit)
  if provider:
    query |= Q(target_provider=provider)

  return InboxMessage.objects.filter(query, is_resolved=False).order_by('-created_at')


def get_inbox_count(user) -> int:
  """
  Zählt die unerledigten InboxMessages für den übergebenen User.
  Ist eine schlanke Variante von get_inbox_messages() die nur COUNT ausführt.

  :param user: Django-User-Instanz
  :return: Anzahl unerledigter Nachrichten
  """
  return get_inbox_messages(user).count()


def get_user_provider(user):
  """
  Returns the provider associated with the user's KiJu profile,
  or None if no profile or no provider is set.

  :param user: user
  :return: Provider instance or None
  """
  from .models.base import UserProfile

  try:
    user_profile = UserProfile.objects.get(user_id=user.id)
    return user_profile.provider
  except UserProfile.DoesNotExist:
    return None


def get_user_org_unit(user):
  """
  Returns the organisational unit associated with the user's KiJu profile,
  or None if no profile or no organisational unit is set.

  :param user: user
  :return: OrgUnit instance or None
  """
  from .models.base import UserProfile

  try:
    user_profile = UserProfile.objects.get(user_id=user.id)
    return user_profile.organisational_unit
  except UserProfile.DoesNotExist:
    return None


def authorized_to_review(user, service=None):
  """
  Checks if the user is authorized to review a service.

  - Superusers and KiJu admins can always review.
  - Normal users can only review if they have an organisational unit assigned
    and (if a service is given) that organisational unit has a matching
    OrgUnitServicePermission for the service's model type.
  - If service is None, only checks whether the user has an
    organisational unit at all.

  :param user: user
  :param service: optional Service instance to check against
  :return: True if the user is authorized to review the service
  """
  if user.is_superuser or is_angebotsdb_admin(user):
    return True

  org_unit = get_user_org_unit(user)
  if not org_unit:
    return False

  if service is None:
    return True

  from .models.base import OrgUnitServicePermission

  service_type = type(service).__name__.lower()
  return OrgUnitServicePermission.objects.filter(
    organisational_unit=org_unit,
    service_type=service_type,
  ).exists()


def authorized_to_edit(user, service=None):
  """
  Checks if the user is authorized to edit/delete a service.

  - Superusers and KiJu admins can always edit.
  - Normal users can only edit if they have a provider assigned
    and (if a service is given) that provider matches the service's host.
  - If service is None (e.g. in CreateView), only checks whether
    the user has a provider at all.

  :param user: user
  :param service: optional Service instance to check against
  :return: True if the user is authorized to edit/delete the service
  """
  if user.is_superuser or is_angebotsdb_admin(user):
    return True

  provider = get_user_provider(user)
  if not provider:
    return False

  if service is None:
    return True

  return provider == service.host


def is_angebotsdb_admin(user):
  """
  checks if passed user is a KIJU admin

  :param user: user
  :return: passed user is a KIJU admin?
  """
  return user.groups.filter(name=ADMIN_GROUP).exists()


def create_draft_copy(service, user):
  """
  Erstellt eine Draft-Copy eines published Service-Objekts.

  - Kopiert alle konkreten Felder außer: id, created_at, updated_at,
    status, published_version.
  - Setzt status='draft' und published_version=service auf der Kopie.
  - Überträgt alle ManyToMany-Felder nach dem Speichern.
  - Das image-Feld (ImageField) wird als Dateipfad kopiert — die Datei
    selbst wird nicht verschoben oder dupliziert.
  - Gibt die gespeicherte Draft-Copy-Instanz zurück.

  :param service: Die published Service-Instanz (Original)
  :param user: Der anfragende User (für Logging)
  :return: Neue, gespeicherte Draft-Copy-Instanz
  """
  import logging

  logger = logging.getLogger(__name__)

  SKIP_FIELDS = {'id', 'created_at', 'updated_at', 'status', 'published_version_id'}

  new = service.__class__()

  for field in service._meta.concrete_fields:
    if field.name in SKIP_FIELDS or field.attname in SKIP_FIELDS:
      continue
    setattr(new, field.attname, getattr(service, field.attname))

  new.status = 'draft'
  new.published_version = service
  new.save()

  for field in service._meta.many_to_many:
    getattr(new, field.name).set(getattr(service, field.name).all())

  # ServiceImage-Einträge kopieren (Dateipfad wird geteilt, nicht dupliziert)
  from .models.services import ServiceImage

  service_type = service.__class__.__name__.lower()
  for img in ServiceImage.objects.filter(service_type=service_type, service_id=service.pk):
    ServiceImage.objects.create(
      service_type=service_type,
      service_id=new.pk,
      image=img.image,
      position=img.position,
    )

  logger.info(
    'Draft-Copy #%s erstellt von User %s für published Service #%s (%s)',
    new.pk,
    user,
    service.pk,
    service.__class__.__name__,
  )
  return new


def get_draft_copy_for_user(service, user):
  """
  Gibt eine bereits existierende aktive Draft-Copy für diesen Service und
  den Provider des Users zurück, oder None wenn keine existiert.

  Verhindert, dass mehrere Draft-Copies desselben Service angelegt werden.

  :param service: Das Original (published) Service-Objekt
  :param user: Der anfragende User
  :return: Existierende Draft-Copy oder None
  """
  provider = get_user_provider(user)
  if provider is None:
    return None

  return service.__class__.objects.filter(
    published_version=service,
    host=provider,
    status__in=['draft', 'in_review', 'revision_needed'],
  ).first()


def apply_draft_to_published(draft, published):
  """
  Überträgt alle inhaltlichen Felder der Draft-Copy auf den published-Datensatz.

  - Kopiert alle konkreten Felder außer: id, created_at, updated_at,
    status, published_version, host.
  - Das image-Feld wird als Dateipfad kopiert. Das alte Bild des Originals
    wird NICHT vom Filesystem gelöscht (Bereinigung ist separates Thema).
  - Überträgt alle ManyToMany-Felder via .set().
  - Setzt published.status = 'published' explizit.
  - Speichert den published-Datensatz.
  - Löscht die Draft-Copy anschließend.

  :param draft: Die freigegebene Draft-Copy
  :param published: Das Original (published) Service-Objekt
  """
  import logging

  logger = logging.getLogger(__name__)

  SKIP_FIELDS = {
    'id',
    'created_at',
    'updated_at',
    'status',
    'published_version_id',
    'host_id',
  }

  for field in draft._meta.concrete_fields:
    if field.attname in SKIP_FIELDS:
      continue
    setattr(published, field.attname, getattr(draft, field.attname))

  published.status = 'published'
  published.save()

  for field in draft._meta.many_to_many:
    getattr(published, field.name).set(getattr(draft, field.name).all())

  # ServiceImage: Alte Bilder des Published löschen, Draft-Bilder umhängen
  from .models.services import ServiceImage

  service_type = draft.__class__.__name__.lower()
  ServiceImage.objects.filter(service_type=service_type, service_id=published.pk).delete()
  ServiceImage.objects.filter(service_type=service_type, service_id=draft.pk).update(
    service_id=published.pk
  )

  draft_pk = draft.pk
  draft.delete()

  logger.info(
    'Draft-Copy #%s auf published Service #%s (%s) übertragen und gelöscht.',
    draft_pk,
    published.pk,
    published.__class__.__name__,
  )


def is_angebotsdb_user(user, only_kiju_user_check=False):
  """
  checks if passed user is a KIJU user
  (and optionally checks if it is a KIJU user only)

  :param user: user
  :param only_kiju_user_check: check if user is a KIJU user only?
  :return: passed user is a KIJU user (only)?
  """
  in_kiju_groups = user.groups.filter(name__in=[ADMIN_GROUP, USERS_GROUP])
  if in_kiju_groups:
    if only_kiju_user_check:
      # if user is a KIJU user only, he is not a member of any other group
      return in_kiju_groups.count() == user.groups.all().count()
    else:
      return True
  return False
