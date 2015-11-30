# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Adherent',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('nom', models.CharField(max_length=45, verbose_name='Nom de famille')),
                ('prenom', models.CharField(max_length=30, verbose_name='Prénom')),
                ('mail', models.EmailField(max_length=150, verbose_name='e-mail de contact')),
                ('chambre', models.CharField(unique=True, max_length=4, verbose_name='Numéros de chambre', validators=[django.core.validators.RegexValidator(message='Erreur: cette chambre ne peut exister', regex='^[A-DH][0-3][01][0-9]$')])),
                ('dateExpiration', models.DateField(default=django.utils.timezone.now, verbose_name="Date de coupure de l'adhérent")),
                ('commentaire', models.TextField(blank=True, verbose_name="Commentaire sur l'adhérent")),
                ('estRezoman', models.BooleanField(default=False, verbose_name='statut de Rezoman')),
                ('estValide', models.BooleanField(default=False, verbose_name="l'adherent est valide")),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Ordinateur',
            fields=[
                ('nom', models.CharField(primary_key=True, max_length=20, serialize=False, verbose_name='nom indice du PC')),
                ('adresseMAC', models.CharField(max_length=17, verbose_name='Adresse MAC', validators=[django.core.validators.RegexValidator(message='Adresse MAC invalide', regex='^([a-f0-9](2):)(5)[a-f0-9](2)$')])),
                ('adresseIP', models.GenericIPAddressField(protocol='IpV4', verbose_name='IP dynamique')),
                ('possesseur', models.ForeignKey(to='module_Adherent.Adherent', verbose_name="Possesseur de l'ordinateur")),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
