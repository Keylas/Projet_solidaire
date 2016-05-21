##Fichier regroupant l'ensemble des classe du module ressourcesAdhérent permettant l'affichage des entité par le module admin de django

# coding=utf8

from django.contrib import admin
from ressourcesAdherent.models import Adherent, Ordinateur, Chambre

##Classe de gestion d'affichage de l'entité Adhérent
class adminAdherent(admin.ModelAdmin):
    ##Liste des paramètre affiché lors de l'affichage de l'ensemble des Adhérents
    list_display = ('nom', 'prenom', 'dateExpiration', 'estValide')
    ##Liste des champs selon lesquelle on peut filtrer les Adhérents
    list_filter = ('estRezoman', 'estValide')
    ##Ordonancement des dates selon les dates d'expirations des adhérents
    date_hierarchy = 'dateExpiration'
    ##Ensemble des champ de tri des entités
    ordering = ('dateExpiration',)
    ##Ensemble des champs dans lesquelle on peut effectuer une recherche
    search_fields = ('nom', 'prenom', 'chambre')
    ##Descripion du type d'entité affiché
    description = "Adrérent du réseau"
    ##Ensemble des champs ne pouvant pas être edité directement avec le module admin
    exclude = ('estValide',)


##Classe de gestion d'affichage de l'entité Ordinateur
class adminOrdinateur(admin.ModelAdmin):
    ##Liste des paramètre affiché lors de l'affichage de l'ensemble des Ordinateurs
    list_display = ('proprietaire', 'adresseIP', 'adresseMAC')
    ##Liste des champs selon lesquelle on peut filtrer les Ordinateurs
    list_filter = ('carteWifi',)
    ##Ensemble des champs dans lesquelle on peut effectuer une recherche
    search_fields = ('proprietaire', 'adresseIP', 'adresseMAC')
    ##Descripion du type d'entité affiché
    description = "Ordinateur autorisé"
    ##Ensemble des champs ne pouvant pas être edité directement avec le module admin
    exclude = ('nomDNS', 'adresseIP')


##Classe de gestion d'affichage de l'entité Chambre
class adminChambre(admin.ModelAdmin):
    ##Liste des paramètre affiché lors de l'affichage de l'ensemble des Chambres
    list_display = ('numero', 'switch', 'port')
    ##Descripion du type d'entité affiché
    description = "Chambre de la résidence"


admin.site.register(Adherent, adminAdherent)  # Link de l'entité Adhérent
admin.site.register(Ordinateur, adminOrdinateur)  # Link de l'entité Ordinateur
admin.site.register(Chambre, adminChambre) # Link de l'entité Chambre
