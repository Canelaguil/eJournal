# Generated by Django 2.1.2 on 2018-10-28 11:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('VLE', '0009_add_selection_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participation',
            name='group',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='VLE.Group'),
        ),
    ]
