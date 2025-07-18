from django.db.models import CharField, EmailField, ImageField, Model, SmallAutoField, TextField


class Host(Model):
  class Meta:
    verbose_name = 'Anbietender'
    verbose_name_plural = 'Anbietende'

  id = SmallAutoField(primary_key=True, verbose_name='ID')
  name = CharField(max_length=255, verbose_name='Bezeichnung')
  description = TextField(verbose_name='Beschreibung')
  logo = ImageField(upload_to='hosts/', verbose_name='Logo')
  address = CharField(max_length=255, verbose_name='Adresse')
  contact_person = CharField(max_length=255, verbose_name='Ansprechpartner')
  email = EmailField(max_length=255, verbose_name='E-Mail')
  phone = CharField(max_length=255, verbose_name='Telefonnummer')

  def __str__(self):
    return self.name
