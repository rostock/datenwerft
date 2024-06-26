# Generated by Django 5.0.4 on 2024-04-04 11:18

from django.db import migrations, models
import toolbox.fields


class Migration(migrations.Migration):

    dependencies = [
        ('bemas', '0007_alter_complaint_dms_link_alter_event_dms_link_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={'get_latest_by': 'updated_at', 'ordering': ['-complaint__id', models.OrderBy(models.F('date'), descending=True, nulls_last=True)], 'verbose_name': 'Journalereignis', 'verbose_name_plural': 'Journalereignisse'},
        ),
        migrations.AlterField(
            model_name='event',
            name='description',
            field=toolbox.fields.NullTextField(blank=True, null=True, verbose_name='Beschreibung'),
        ),
    ]
