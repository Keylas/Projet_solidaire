from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = patterns('',
    url(r'^connexion$', auth_views.login, {'template_name': 'connexion.html'}),
    url(r'^deconnexion$', auth_views.logout, {'next_page': '/gestion/connexion'}, name="lien_logout"),
    url(r'^accueil$', views.ListeLog.as_view(), name="page_accueil"),
    url(r'^payement$', views.ListePayement.as_view(), name="page_payement"),
    url(r'^editionP/(?P<id>[0-9]+)$', views.editerPayement, name="page_editionP"),
    url(r'^creationP/(?P<adhrId>[0-9]+)$', views.creerPayement, name="page_creationP"),
    url(r'^etiderEtatP/(?P<payement_id>[0-9]+)$', views.changerEtatPayement, name="page_etatP"),
    url(r'^utilisateur$', views.ListeUtilisateur.as_view(), name="page_utilisateur"),
    url(r'^supprimerUtilisateur/(?P<utilisateur_id>[0-9]+)$', views.supprimerUtilisateur, name="supprUtilisateur"),
    url(r'^creerUtilisateur$', views.creer_utilisateur, name="creationU"),
    url(r'^editerUtilisateur/(?P<userId>[0-9]+)$', views.editerUtilisateur, name="page_editionU")
)

