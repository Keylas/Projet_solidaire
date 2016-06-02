##Fichier regroupant l'ensemble des classe du module gestion permettant l'affichage des entité par le module admin de django


# coding=utf8

from django.contrib import admin
from gestion.models import Log, Utilisateur, Payement, Constante


# Register your models here.

##Classe de gestion d'affichage de l'entité Log
class adminLog(admin.ModelAdmin):
    ##Liste des elements du Log à afficher
    list_display = ('date', 'editeur', 'apercu_description')
    ##Liste des elements qui permettre un filtrage selon leurs valeurs
    list_filter = ('date', 'editeur')
    ##Ordonancement des dates selon les dates des logs
    date_hierarchy = 'date'
    ##Ensemble des champ de tri des logs
    ordering = ('date',)
    ##Liste des champs permettant une recherches dans leurs valeurs
    search_fields = ('description',)
    ##Liste des champs qui sont éditable par le module admin
    fields = ('editeur', 'description')

    ##Fonction qui permet de tronquer la description du log.
    #@param self Reférence vers la l'entité d'affichage
    #@param log Log à tronquer si necessaire
    def apercu_description(self, log):
        text = log.description[0:40]
        if len(log.description) > 40:
            return '%s…' % text
        else:
            return text

    ##Chaine indiquant le rôle de la colonne 'aprecu_description'
    apercu_description.short_description = "Description du log"


##Classe de gestion d'affichage de l'entité Payement
class adminPayement(admin.ModelAdmin):
    ##Liste des elements du Payement à afficher
    list_display = ('beneficiaire', 'credit', 'montantRecu', 'etat')
    ##Liste des eléments du Payement qui permettre un filtrage selon leurs valeurs
    list_filter = ('dateCreation', 'etat')
    ##Ordonancement des dates selon les dates  de création des payements
    date_hierarchy = 'dateCreation'
    ##Ensemble des champ de tri des payements
    ordering = ('dateCreation',)
    ##Liste des champs qui accepte une recherche dans leurs valeurs
    search_fields = ('credit', 'montantRecu')
    ##Liste des champs à exclure de la modification par le module admin.
    exclude = ('etat',)


##Activation de l'entité Log dans le module admin, avec les paramètres adminLog
admin.site.register(Log, adminLog)
##Activation de l'entité Utilisateur dans le module admin
admin.site.register(Utilisateur)
##Activation de l'entité Payement dans le module admin, avec les paramètres adminPayement
admin.site.register(Payement, adminPayement)
##Activation de l'entité Constante dans le module admin
admin.site.register(Constante)
