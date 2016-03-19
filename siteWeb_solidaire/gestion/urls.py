from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = patterns('',
    url(r'^connexion$', auth_views.login, {'template_name' : 'connexion.html'}),
    url(r'^deconnexion$', auth_views.logout, {'next_page' : '/gestion/connexion'}, name="lien_logout"),
    url(r'^accueil$', views.ListeLog.as_view(), name="page_accueil"),
    url(r'^payement$', views.ListePayement.as_view(), name="page_payement"),
    url(r'^editionP/(?P<id>[0-9]+)$', views.editerPayement, name="page_editionP"),
    url(r'^creationP/(?P<adhrId>[0-9]+)$', views.creerPayement, name="page_creationP"),
    url(r'^utilisateur$', views.ListeUtilisateur.as_view(), name="page_utilisateur"),
)

