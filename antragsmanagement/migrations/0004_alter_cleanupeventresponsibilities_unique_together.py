# Generated by Django 5.0.7 on 2024-07-12 12:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('antragsmanagement', '0003_alter_cleanupeventresponsibilities_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='cleanupeventresponsibilities',
            unique_together={('cleanupevent_request', 'authority'), ('cleanupevent_request', 'main')},
        ),
    ]