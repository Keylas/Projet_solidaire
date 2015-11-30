# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('description', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Payement',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('dateExecution', models.DateTimeField(auto_now_add=True)),
                ('montantFictif', models.DecimalField(decimal_places=2, verbose_name='Montant à créditer', max_digits=6)),
                ('montantReel', models.DecimalField(decimal_places=2, verbose_name='Montant réel payé', max_digits=6)),
                ('commentaire', models.TextField(verbose_name='Commentaire du créateur, à remplir si les deux montants sont différents', null=True)),
                ('banque', models.CharField(max_length=42, null=True)),
                ('etat', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Utilisateur',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('role', models.IntegerField(default=0, verbose_name='statut du rezoman')),
                ('user', models.OneToOneField(verbose_name='identifiants de connexion', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='log',
            name='editeur',
            field=models.ForeignKey(to='gestion.Utilisateur'),
            preserve_default=True,
        ),
    ]
