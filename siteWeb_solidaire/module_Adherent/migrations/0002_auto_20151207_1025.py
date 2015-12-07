# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('module_Adherent', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordinateur',
            name='adresseMAC',
            field=models.CharField(verbose_name='Adresse MAC', max_length=17, validators=[django.core.validators.RegexValidator(message='Adresse MAC invalide', regex='^([a-f0-9]{2}:){5}[a-f0-9]{2}$')]),
        ),
    ]
