import django.contrib.postgres.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
  initial = True

  dependencies = [
    ('contenttypes', '0002_remove_content_type_name'),
  ]

  operations = [
    migrations.CreateModel(
      name='Subsets',
      fields=[
        ('id', models.AutoField(primary_key=True, serialize=False)),
        ('created_at', models.DateTimeField(auto_now=True)),
        ('pk_field', models.CharField(max_length=255)),
        ('pks',
         django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=36),
                                                   size=None)),
        ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    to='contenttypes.contenttype')),
      ],
      options={
        'verbose_name': 'Subset',
        'verbose_name_plural': 'Subsets',
      },
    ),
  ]
