from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Adherent

# Create your views here.

class ListeAdherent(ListView):
    model = Adherent
    context_object_name = "liste_Adherent"
    template_name="TAdherent.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ListeAdherent, self).dispatch(*args, **kwargs)
