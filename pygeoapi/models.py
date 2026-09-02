from django.core.exceptions import ValidationError
from django.db.models import (
  CASCADE,
  PROTECT,
  CheckConstraint,
  F,
  ForeignKey,
  Model,
  Q,
  TextChoices,
  UniqueConstraint,
)
from django.db.models.fields import (
  AutoField,
  BigIntegerField,
  BooleanField,
  CharField,
  PositiveSmallIntegerField,
)
from django.utils.translation import gettext_lazy as _


class StorageCrs(TextChoices):
  EPSG_25833 = 'https://www.opengis.net/def/crs/EPSG/0/25833', _('EPSG:25833')
  EPSG_4326 = 'https://www.opengis.net/def/crs/EPSG/0/4326', _('EPSG:4326')
  CRS_84 = 'https://www.opengis.net/def/crs/OGC/0/CRS84', _('CRS:84')


class DatabaseConnection(Model):
  id = AutoField(verbose_name=_('ID'), primary_key=True, editable=False)
  host = CharField(verbose_name=_('Host'), max_length=100)
  port = PositiveSmallIntegerField(verbose_name=_('Port'), default=5432)
  dbname = CharField(verbose_name=_('Datenbank'), max_length=100)
  user = CharField(verbose_name=_('Benutzername'), max_length=100)
  password = CharField(verbose_name=_('Passwort'), max_length=100)

  class Meta:
    db_table = 'pygeoapi_database_connection'
    ordering = ['host', 'dbname', 'user']
    verbose_name = _('Datenbankverbindung')
    verbose_name_plural = _('Datenbankverbindungen')

  def __str__(self):
    return f'{self.host} → {self.dbname} → {self.user}'


class Collection(Model):
  id = AutoField(verbose_name=_('ID'), primary_key=True, editable=False)
  deactivated = BooleanField(verbose_name='deaktiviert')
  service_id = BigIntegerField(unique=True)
  database_connection = ForeignKey(
    DatabaseConnection,
    on_delete=PROTECT,
    related_name='collection_database_connections',
    verbose_name=_('Datenbankverbindung'),
  )
  schema = CharField(verbose_name=_('Name des Schemas'), max_length=100)
  table = CharField(verbose_name=_('Name der/des Tabelle/Views'), max_length=100)
  id_field = CharField(verbose_name=_('Name des ID-Attributs'), max_length=100)
  title_field = CharField(
    verbose_name=_('Name des Attributs mit (möglichst eindeutiger) Bezeichnung'),
    max_length=100,
  )
  geom_field = CharField(verbose_name=_('Name des Geometrie-Attributs'), max_length=100)
  storage_crs = CharField(
    choices=StorageCrs.choices,
    verbose_name=_('Koordinatenreferenzsystem der Geometrie'),
  )

  class Meta:
    db_table = 'pygeoapi_collection'
    ordering = ['service_id']
    verbose_name = _('Kollektion')
    verbose_name_plural = _('Kollektionen')

  def __str__(self):
    return f'{self.id}'


class Role(Model):
  """
  role catalog entry with optional single-parent inheritance (Rolle)
  """

  # reference data, not an identity/membership table: no reference to users.
  # `identifier` mirrors the identity provider verbatim (no case folding).
  # see hilfe/pygeoapi/rollenkatalog.md for identifier coupling and delete behaviour
  id = AutoField(verbose_name=_('ID'), primary_key=True, editable=False)
  identifier = CharField(
    verbose_name=_('Bezeichner (wie im Identity Provider)'),
    max_length=255,
    unique=True,
  )
  label = CharField(verbose_name=_('Bezeichnung'), max_length=255)
  parent = ForeignKey(
    'self',
    on_delete=PROTECT,
    null=True,
    blank=True,
    related_name='role_children',
    verbose_name=_('Eltern-Rolle'),
  )

  class Meta:
    db_table = 'pygeoapi_role'
    ordering = ['identifier']
    verbose_name = _('Rolle')
    verbose_name_plural = _('Rollen')
    constraints = [
      CheckConstraint(
        condition=~Q(parent=F('id')),
        name='pygeoapi_role_no_self_parent',
      ),
    ]

  def __str__(self):
    return f'{self.label} ({self.identifier})'

  def clean(self):
    """
    reject self-reference and inheritance cycles at model level
    """
    super().clean()
    if self.parent_id is None:
      return
    if self.parent_id == self.pk:
      raise ValidationError({'parent': _('Eine Rolle kann nicht ihre eigene Eltern-Rolle sein.')})
    # walk up the parent chain; `visited` guards against an endless loop should
    # the data ever contain a pre-existing cycle
    visited = set()
    ancestor = self.parent
    while ancestor is not None:
      if ancestor.pk == self.pk:
        raise ValidationError(
          {
            'parent': _(
              'Diese Eltern-Rolle würde eine ringförmige Vererbung erzeugen; '
              'die Rechte ließen sich dann nicht mehr eindeutig auflösen.'
            )
          }
        )
      if ancestor.pk in visited:
        break
      visited.add(ancestor.pk)
      ancestor = ancestor.parent

  def save(self, *args, **kwargs):
    # Django does not call full_clean() on save(); without this the clean()
    # cycle check would be bypassed by objects.create(), the shell and tests.
    # bulk_create() skips save() and thus this check (deliberate limit).
    self.full_clean()
    super().save(*args, **kwargs)


class CollectionAttribute(Model):
  """
  inventory of the attribute names a collection's source table/view exposes
  (Attributinventar)
  """

  # mirror of a foreign table's attribute names inside the Datenwerft database.
  # on_delete=CASCADE: deleting a collection takes its whole inventory (and the
  # permissions later hanging off it) with it instead of blocking the delete.
  # populating the inventory: DH-77, assigning per-attribute read rights: DH-74.
  # model rationale: docs/pygeoapi/rechtesystem.md
  # behaviour promised to users: hilfe/pygeoapi/attributinventar.md
  id = AutoField(verbose_name=_('ID'), primary_key=True, editable=False)
  collection = ForeignKey(
    Collection,
    on_delete=CASCADE,
    related_name='attributes',
    verbose_name=_('Kollektion'),
  )
  name = CharField(verbose_name=_('Name des Attributs'), max_length=100)
  # written by the reconciliation (DH-77) from the column list the collection
  # form already loads; only stored and displayed, never interpreted
  data_type = CharField(
    verbose_name=_('Datentyp in der Quelle'),
    max_length=100,
    blank=True,
    default='',
  )
  is_present = BooleanField(
    verbose_name=_('in der Quelle vorhanden'),
    default=True,
  )

  class Meta:
    db_table = 'pygeoapi_collection_attribute'
    ordering = ['collection', 'name']
    verbose_name = _('Attribut einer Kollektion')
    verbose_name_plural = _('Attribute einer Kollektion')
    constraints = [
      UniqueConstraint(
        fields=['collection', 'name'],
        name='pygeoapi_collection_attribute_unique_name_per_collection',
      ),
    ]

  def __str__(self):
    return f'{self.collection} → {self.name}'

  def save(self, *args, **kwargs):
    # Django does not call full_clean() on save(); calling it here surfaces a
    # duplicate (collection, name) as a ValidationError instead of an
    # IntegrityError, mirroring Role.
    # bulk_create() skips save() and thus this check (deliberate limit).
    self.full_clean()
    super().save(*args, **kwargs)


class AttributeReadPermission(Model):
  """
  read permission of exactly one role on exactly one inventoried attribute
  (Leserecht an einem Attribut)
  """

  # the existence of a row IS the permission: there is deliberately no
  # readable/granted flag, which makes deny-by-default structural.
  # on_delete=CASCADE on both sides keeps the promises the help pages already
  # give: deleting a role takes its permissions (rollenkatalog.md), deleting a
  # collection takes its inventory and with it the permissions
  # (attributinventar.md).
  # Collection.id_field and Collection.geom_field are not subject to permission
  # assignment: in the GeoJSON response they sit at root level ('id',
  # 'geometry'), not below 'properties', and are always delivered.
  # model rationale: docs/pygeoapi/rechtesystem.md
  # behaviour promised to users: hilfe/pygeoapi/leserechte.md
  id = AutoField(verbose_name=_('ID'), primary_key=True, editable=False)
  role = ForeignKey(
    Role,
    on_delete=CASCADE,
    related_name='read_permissions',
    verbose_name=_('Rolle'),
  )
  attribute = ForeignKey(
    CollectionAttribute,
    on_delete=CASCADE,
    related_name='read_permissions',
    verbose_name=_('Attribut'),
  )

  class Meta:
    db_table = 'pygeoapi_attribute_read_permission'
    ordering = ['role', 'attribute']
    verbose_name = _('Leserecht an einem Attribut')
    verbose_name_plural = _('Leserechte an Attributen')
    constraints = [
      UniqueConstraint(
        fields=['role', 'attribute'],
        name='pygeoapi_attribute_read_permission_unique_role_attribute',
      ),
    ]

  def __str__(self):
    return f'{self.role} → {self.attribute}'

  @property
  def is_effective(self):
    """
    whether the permission currently has any effect, i.e. whether the attribute
    it refers to is still present in the source; a permission on an attribute
    that has disappeared is kept, but does not grant anything

    reads self.attribute, so iterate with select_related('attribute')
    """
    return self.attribute.is_present

  def save(self, *args, **kwargs):
    # Django does not call full_clean() on save(); calling it here surfaces a
    # duplicate (role, attribute) as a ValidationError instead of an
    # IntegrityError and makes ForeignKey.validate() reject a role or inventory
    # entry that does not exist, mirroring Role (DH-63).
    # bulk_create() skips save() and thus this check (deliberate limit).
    self.full_clean()
    super().save(*args, **kwargs)
