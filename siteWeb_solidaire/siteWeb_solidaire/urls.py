#Fichier urls de siteWeb_solidaire

from django.conf.urls import patterns, include, url
from django.contrib import admin
<<<<<<< HEAD
from gestion import views as g_views
=======
from ressourcesAdherent import views
>>>>>>> branch 'Developpement_models_suite' of https://github.com/Keylas/projet_solidaire

urlpatterns = patterns('',
    # Examples:
    url(r'^onTest$', g_views.test),

    url(r'^admin/', include(admin.site.urls)),
    #url(r'^adherents/', include('ressourceAdherent.urls')),
    url(r'^gestion/', include('gestion.urls')),
    #url(r'^services/', include('services.urls')),
)
