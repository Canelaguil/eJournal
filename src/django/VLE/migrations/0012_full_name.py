# Generated by Django 2.1.2 on 2018-11-06 15:06

from django.db import migrations


def combine_names(apps, schema_editor):
    User = apps.get_model('VLE', 'User')
    for user in User.objects.all():
        user.full_name = '%s %s' % (user.first_name, user.last_name)
        user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('VLE', '0012_user_full_name'),
    ]

    operations = [
        migrations.RunPython(combine_names),
    ]
