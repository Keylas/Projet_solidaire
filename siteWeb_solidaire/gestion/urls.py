from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = patterns('',
    url(r'^connexion$', auth_views.login, {'template_name' : 'connexion.html'}),
    url(r'^deconnexion$', auth_views.logout, {'next_page' : '/gestion/connexion'}, name="lien_logout"),
    url(r'^accueil$', views.ListeLog.as_view(), name="page_accueil"),
)

