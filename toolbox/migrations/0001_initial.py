from django.contrib.postgres.fields import ArrayField
from django.db import migrations, models
from django.db.models.deletion import CASCADE


class Migration(migrations.Migration):
  initial = True

  dependencies = [
    ('contenttypes', '0002_remove_content_type_name')
  ]

  operations = [
    migrations.CreateModel(
      name='Subsets',
      fields=[
        ('id', models.AutoField(primary_key=True, serialize=False)),
        ('created_at', models.DateTimeField(auto_now=True)),
        ('model', models.ForeignKey(on_delete=CASCADE, to='contenttypes.contenttype')),
        ('pk_field', models.CharField(max_length=255)),
        ('pk_values', ArrayField(base_field=models.CharField(max_length=36), size=None))
      ],
      options={
        'verbose_name': 'Subset',
        'verbose_name_plural': 'Subsets'
      }
    )
  ]
