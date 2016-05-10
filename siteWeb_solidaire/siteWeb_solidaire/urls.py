#Fichier urls de siteWeb_solidaire

from django.conf.urls import include, url
from django.contrib import admin
from gestion import views as g_views


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^adherents/', include('ressourcesAdherent.urls')),
    url(r'^gestion/', include('gestion.urls')),
    url(r'^services/', include('services.urls'))
]
