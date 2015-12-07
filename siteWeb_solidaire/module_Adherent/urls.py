#Fichier urls de module_Adherent

from django.conf.urls import patterns, include, url
from django.contrib import admin
from . import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'siteWeb_solidaire.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.liste_adherent),
    url(r'^adherent/(?P<id_adherent>\d+)', views.voir_adherent),
)
