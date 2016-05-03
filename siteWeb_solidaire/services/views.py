from django.shortcuts import render, get_object_or_404, redirect
from ressourcesAdherent.models import Ordinateur
from gestion.models import Utilisateur, Log
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from .models import Mailing

class ListeDNS(ListView):
    #model = Ordinateur
    context_object_name = "liste_ordinateur"
    template_name = "TNomDNS.html"
    ordering = ['nomDNS']
    paginate_by = 50

    # Fonction qui sert a demander une session pour accéder au pages de la classe
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ListeDNS, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        filtre = self.request.GET.get('the_search', '')
        if(filtre == ''):
            return Ordinateur.objects.all().order_by('nomDNS')
        return Ordinateur.objects.filter(Q(nomDNS__icontains=filtre) | Q(adresseMAC__icontains=filtre)).order_by('nomDNS')


@login_required
def changeDNSactif(request, ordiId):
    ordi = get_object_or_404(Ordinateur, pk=ordiId)
    ordi.DNSactif = not ordi.DNSactif
    ordi.save()
    Log.create(editeur=Utilisateur.getUtilisateur(request.user), description="L\'entrée DNS {0} à été mis à jour".format(ordi.nomDNS))
    return redirect('page_DNS')

class MailingList(ListView):
    #model = Mailing
    context_object_name = "liste_mailing"
    template_name = "TMailing.html"
    paginate_by = 25

    # Fonction qui sert a demander une session pour accéder au pages de la classe
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MailingList, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        filtre = self.request.GET.get('the_search', '')
        if(filtre == ''):
            return Mailing.objects.all().order_by('adresse')
        return Mailing.objects.filter(Q(adresse__icontains=filtre) | Q(referant__nom__icontains=filtre) |
                                      Q(referant__prenom__icontains=filtre)).order_by('adresse')

def creerMailing(request):

    return redirect('page_mailing')