# Generated by Django 5.0.6 on 2024-07-17 02:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('console', '0009_team_member_user_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='team_member',
            name='first_login',
            field=models.BooleanField(default=True),
        ),
    ]
