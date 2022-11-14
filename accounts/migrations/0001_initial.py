from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
  initial = True

  dependencies = [
    ('auth', '0012_alter_user_first_name_max_length'),
  ]

  operations = [
    migrations.CreateModel(
      name='UserAuthToken',
      fields=[
        ('user',
         models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True,
                              serialize=False, to='auth.user')),
        ('session_token', models.CharField(max_length=40, unique=True)),
        ('url_token', models.CharField(max_length=24, unique=True)),
        ('email_token', models.CharField(max_length=16)),
        ('created_at', models.DateTimeField(auto_now=True)),
      ],
      options={
        'verbose_name': 'AuthToken',
        'verbose_name_plural': 'AuthTokens',
      },
    ),
  ]
