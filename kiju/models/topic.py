from django.db.models import CharField, Model


class Topic(Model):
  name = CharField(max_length=255, verbose_name='Bezeichnung')

  def __str__(self):
    return self.name
