from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views

urlpatterns = patterns('',
    url(r'^connexion$', auth_views.login, {'template_name' : 'connexion.html', 'extra_context' : {'next' : 'connexion'}}),
    url(r'^deconnexion$', auth_views.logout, {'next_page': 'connexion'}),
)
