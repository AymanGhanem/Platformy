# Generated by Django 4.0.4 on 2022-05-04 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_service_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='state',
            field=models.CharField(choices=[('pending', 'Pending'), ('running', 'Running'), ('stopping', 'Stopping'), ('stopped', 'Stopped'), ('shutting-down', 'Shutting-down'), ('terminated', 'Terminated')], max_length=255),
        ),
    ]
