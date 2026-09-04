from dataclasses import dataclass, field

from django.db import transaction

from pygeoapi.models import CollectionAttribute


@dataclass
class ReconcileResult:
  """
  summary of a single reconcile, as attribute names per outcome (Ergebnis eines
  Abgleichs)

  the categories are not mutually exclusive: a reappeared attribute whose data
  type changed in the meantime is named in both lists
  """

  added: list[str] = field(default_factory=list)
  vanished: list[str] = field(default_factory=list)
  reappeared: list[str] = field(default_factory=list)
  retyped: list[str] = field(default_factory=list)

  @property
  def has_changes(self):
    return bool(self.added or self.vanished or self.reappeared or self.retyped)


def reconcile_collection_inventory(collection, columns) -> ReconcileResult:
  """
  reconciles a collection's attribute inventory against the given source columns

  Adds missing attributes, flags attributes no longer in the source as
  ``is_present=False`` without deleting them, clears that flag when one
  reappears and carries a changed data type forward; unchanged entries are left
  untouched.

  The columns are not read from the source here – they reach this function
  validated from ``CollectionForm.clean_reconcile_columns()``. See
  ``docs/pygeoapi/rechtesystem.md`` for the data path and its accepted risk.

  :param collection: collection whose inventory is reconciled
  :param columns: source columns as dicts of ``name`` and ``type``
  :return: summary of added, vanished, reappeared and retyped attribute names
  """
  result = ReconcileResult()
  # never read as "every attribute vanished"; the caller reports the cause
  if not columns:
    return result
  types_by_name = {column['name']: column['type'] for column in columns}
  with transaction.atomic():
    existing = {attribute.name: attribute for attribute in collection.attributes.all()}
    to_create, vanished, reappeared, retyped = [], [], [], []
    for name, data_type in types_by_name.items():
      if name not in existing:
        to_create.append(
          CollectionAttribute(collection=collection, name=name, data_type=data_type)
        )
    for name, attribute in existing.items():
      if name not in types_by_name:
        if attribute.is_present:
          vanished.append(attribute)
        continue
      if not attribute.is_present:
        reappeared.append(attribute)
      if attribute.data_type != types_by_name[name]:
        attribute.data_type = types_by_name[name]
        retyped.append(attribute)
    # set-based, so that the number of queries does not grow with the number of
    # attributes: one read plus at most four writes
    if to_create:
      # skips full_clean(); why that is safe here: docs/pygeoapi/rechtesystem.md
      CollectionAttribute.objects.bulk_create(to_create, ignore_conflicts=True)
    if vanished:
      pks = [attribute.pk for attribute in vanished]
      CollectionAttribute.objects.filter(pk__in=pks).update(is_present=False)
    if reappeared:
      pks = [attribute.pk for attribute in reappeared]
      CollectionAttribute.objects.filter(pk__in=pks).update(is_present=True)
    if retyped:
      CollectionAttribute.objects.bulk_update(retyped, ['data_type'])
  # sorted, so that the reported names do not depend on the order the browser sent
  result.added = sorted(attribute.name for attribute in to_create)
  result.vanished = sorted(attribute.name for attribute in vanished)
  result.reappeared = sorted(attribute.name for attribute in reappeared)
  result.retyped = sorted(attribute.name for attribute in retyped)
  return result
