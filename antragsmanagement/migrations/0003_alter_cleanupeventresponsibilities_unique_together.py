# Generated by Django 5.0.7 on 2024-07-12 12:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('antragsmanagement', '0002_data'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='cleanupeventresponsibilities',
            unique_together={('cleanupevent_request', 'main')},
        ),
    ]