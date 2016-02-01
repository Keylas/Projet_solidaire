#Fichier urls de siteWeb_solidaire

from django.conf.urls import patterns, include, url
from django.contrib import admin
from ressourcesAdherent import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'siteWeb_solidaire.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    #url(r'^adherents/', include('ressourceAdherent.urls')),
    url(r'^gestion/', include('gestion.urls')),
    #url(r'^services/', include('services.urls')),
)
