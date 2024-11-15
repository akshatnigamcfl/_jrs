# Generated by Django 5.0.6 on 2024-07-27 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('console', '0011_booking_bride_email_id_booking_bride_date_of_birth_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='bride_Email_id',
        ),
        migrations.RemoveField(
            model_name='client',
            name='bride_date_of_birth',
        ),
        migrations.RemoveField(
            model_name='client',
            name='bride_name',
        ),
        migrations.RemoveField(
            model_name='client',
            name='groom_Email_id',
        ),
        migrations.RemoveField(
            model_name='client',
            name='groom_contact_number',
        ),
        migrations.RemoveField(
            model_name='client',
            name='groom_date_of_birth',
        ),
        migrations.RemoveField(
            model_name='client',
            name='groom_name',
        ),
        migrations.RemoveField(
            model_name='client',
            name='wedding_date',
        ),
        migrations.RemoveField(
            model_name='client',
            name='wedding_venue',
        ),
        migrations.AlterField(
            model_name='booking',
            name='bride_date_of_birth',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='groom_date_of_birth',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='wedding_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
