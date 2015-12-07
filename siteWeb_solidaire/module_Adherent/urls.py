#Fichier urls du module adhérents

from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'siteWeb_solidaire.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    
    url(r'^$', views.liste_adherent), #Page générale des adhérents
    url(r'^adherent/(?P<id_adherent>\d+)$', views.voir_adherent), #Page spécifique à un adhérent

)
