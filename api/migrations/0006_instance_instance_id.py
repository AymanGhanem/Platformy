# Generated by Django 4.0.4 on 2022-04-28 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_user_email_alter_user_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='instance',
            name='instance_id',
            field=models.CharField(default='22', max_length=255),
            preserve_default=False,
        ),
    ]
