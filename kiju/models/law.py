from django.db.models import CharField, Model, SmallAutoField


class Law(Model):
  id = SmallAutoField(primary_key=True, verbose_name='ID')
  law_book = CharField(
    verbose_name='Gesetzesbuch (Abkürzung, z.B. SGB VIII)',
    max_length=25,
    blank=False,
    null=False,
  )
  paragraph = CharField(
    verbose_name='Paragraoh (ohne §, z.B. 8a)',
    max_length=25,
    blank=False,
    null=False,
  )

  def __str__(self):
    return f'{self.paragraph} {self.law_book}'
