# Generated by Django 3.1 on 2023-02-16 17:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('country', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='country',
            options={'verbose_name': 'country', 'verbose_name_plural': 'countries'},
        ),
    ]