from django.shortcuts import render, get_object_or_404, redirect
from ressourcesAdherent.models import Ordinateur
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class ListeDNS(ListView):
    model = Ordinateur
    context_object_name = "liste_ordinateur"
    template_name = "TNomDNS.html"

    # Fonction qui sert a demander une session pour accéder au pages de la classe
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ListeDNS, self).dispatch(*args, **kwargs)

@login_required
def changeDNSactif(request, ordiId):
    ordi = get_object_or_404(Ordinateur, pk=ordiId)
    ordi.DNSactif = not ordi.DNSactif
    ordi.save()
    return redirect('page_DNS')

