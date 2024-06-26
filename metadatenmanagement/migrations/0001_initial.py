# Generated by Django 5.0.6 on 2024-06-11 06:28

import django.core.validators
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CodelistUpdateFrequency',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Erstellung')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='letzte Änderung')),
                ('namespace', models.URLField(blank=True, null=True, validators=[django.core.validators.RegexValidator(message='Texte dürfen keine Akute (´) enthalten. Stattdessen muss der typographisch korrekte Apostroph (’) verwendet werden.', regex='^(?!.*´).*$'), django.core.validators.RegexValidator(message='Texte dürfen keine doppelten Schreibmaschinensatz-Anführungszeichen (") enthalten. Stattdessen müssen die typographisch korrekten Anführungszeichen („“) verwendet werden.', regex='^(?!.*\\").*$'), django.core.validators.RegexValidator(message="Texte dürfen keine einfachen Schreibmaschinensatz-Anführungszeichen (') enthalten. Stattdessen muss der typographisch korrekte Apostroph(’) verwendet werden.", regex="^(?!.*\\').*$"), django.core.validators.RegexValidator(message='Texte dürfen keine doppelten Leerzeichen enthalten.', regex='^(?!.*  ).*$'), django.core.validators.RegexValidator(message='Texte dürfen keine Gravis (`) enthalten. Stattdessen muss der typographisch korrekte Apostroph (’) verwendet werden.', regex='^(?!.*`).*$')], verbose_name='Namensraum')),
                ('code', models.CharField(unique=True, validators=[django.core.validators.RegexValidator(message='Texte dürfen keine Akute (´) enthalten. Stattdessen muss der typographisch korrekte Apostroph (’) verwendet werden.', regex='^(?!.*´).*$'), django.core.validators.RegexValidator(message='Texte dürfen keine doppelten Schreibmaschinensatz-Anführungszeichen (") enthalten. Stattdessen müssen die typographisch korrekten Anführungszeichen („“) verwendet werden.', regex='^(?!.*\\").*$'), django.core.validators.RegexValidator(message="Texte dürfen keine einfachen Schreibmaschinensatz-Anführungszeichen (') enthalten. Stattdessen muss der typographisch korrekte Apostroph(’) verwendet werden.", regex="^(?!.*\\').*$"), django.core.validators.RegexValidator(message='Texte dürfen keine doppelten Leerzeichen enthalten.', regex='^(?!.*  ).*$'), django.core.validators.RegexValidator(message='Texte dürfen keine Gravis (`) enthalten. Stattdessen muss der typographisch korrekte Apostroph (’) verwendet werden.', regex='^(?!.*`).*$')], verbose_name='Code')),
                ('title', models.CharField(validators=[django.core.validators.RegexValidator(message='Texte dürfen keine Akute (´) enthalten. Stattdessen muss der typographisch korrekte Apostroph (’) verwendet werden.', regex='^(?!.*´).*$'), django.core.validators.RegexValidator(message='Texte dürfen keine doppelten Schreibmaschinensatz-Anführungszeichen (") enthalten. Stattdessen müssen die typographisch korrekten Anführungszeichen („“) verwendet werden.', regex='^(?!.*\\").*$'), django.core.validators.RegexValidator(message="Texte dürfen keine einfachen Schreibmaschinensatz-Anführungszeichen (') enthalten. Stattdessen muss der typographisch korrekte Apostroph(’) verwendet werden.", regex="^(?!.*\\').*$"), django.core.validators.RegexValidator(message='Texte dürfen keine doppelten Leerzeichen enthalten.', regex='^(?!.*  ).*$'), django.core.validators.RegexValidator(message='Texte dürfen keine Gravis (`) enthalten. Stattdessen muss der typographisch korrekte Apostroph (’) verwendet werden.', regex='^(?!.*`).*$')], verbose_name='Bezeichnung')),
                ('description', models.CharField(blank=True, null=True, validators=[django.core.validators.RegexValidator(message='Texte dürfen keine Akute (´) enthalten. Stattdessen muss der typographisch korrekte Apostroph (’) verwendet werden.', regex='^(?!.*´).*$'), django.core.validators.RegexValidator(message='Texte dürfen keine doppelten Schreibmaschinensatz-Anführungszeichen (") enthalten. Stattdessen müssen die typographisch korrekten Anführungszeichen („“) verwendet werden.', regex='^(?!.*\\").*$'), django.core.validators.RegexValidator(message="Texte dürfen keine einfachen Schreibmaschinensatz-Anführungszeichen (') enthalten. Stattdessen muss der typographisch korrekte Apostroph(’) verwendet werden.", regex="^(?!.*\\').*$"), django.core.validators.RegexValidator(message='Texte dürfen keine doppelten Leerzeichen enthalten.', regex='^(?!.*  ).*$'), django.core.validators.RegexValidator(message='Texte dürfen keine Gravis (`) enthalten. Stattdessen muss der typographisch korrekte Apostroph (’) verwendet werden.', regex='^(?!.*`).*$')], verbose_name='Beschreibung')),
            ],
            options={
                'verbose_name': 'Aktualisierungshäufigkeit',
                'verbose_name_plural': 'Aktualisierungshäufigkeiten',
                'db_table': 'codelist_updatefrequency',
                'ordering': ['title'],
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
    ]
