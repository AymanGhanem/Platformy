# Generated by Django 4.0.4 on 2022-04-28 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_application_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='application_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='service',
            name='price_unit_per_hour',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
    ]
