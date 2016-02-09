from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = patterns('',
    url(r'^listeAdherent$', views.ListeAdherent.as_view(), name="affichageAdherent")
)