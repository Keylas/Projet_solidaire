from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = patterns('',
    url(r'^listeAdherent$', views.ListeAdherent.as_view(), name="affichageAdherent"), # page pour afficher les adherents
    url(r'^rezotage$', views.rezotage, name="pageRezotage"), # page de rezotage d'un nouvel adherent
    url(r'listeOrdinateur', views.ListeOrdinateur.as_view(), name="affichageOrdinateur"), # page pour afficher les ordinateurs
)