from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views

urlpatterns = patterns('',
<<<<<<< HEAD
    url(r'^connexion$', auth_views.login, {'template_name' : 'connexion.html'}),
    url(r'^deconnexion$', auth_views.logout, {'next_page' : '/gestion/connexion'}),
=======
    url(r'^connexion$', auth_views.login, {'template_name' : 'connexion.html', 'extra_context' : {'next' : 'connexion'}}),
    url(r'^deconnexion$', auth_views.logout, {'next_page': 'connexion'}),
>>>>>>> branch 'Developpement_models_suite' of https://github.com/Keylas/projet_solidaire
)
