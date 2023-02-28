# Generated by Django 3.1 on 2023-02-16 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country_name', models.CharField(max_length=255, unique=True)),
                ('shipping_cost', models.DecimalField(decimal_places=2, max_digits=6)),
            ],
        ),
    ]