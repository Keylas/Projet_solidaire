from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Adherent, Ordinateur
from gestion.models import Payement, Utilisateur, Log, ConstanteNotFind
from .forms import RezotageForm

# Create your views here.

class ListeAdherent(ListView):
    model = Adherent
    context_object_name = "liste_Adherent"
    template_name="TAdherent.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ListeAdherent, self).dispatch(*args, **kwargs)

@login_required
def rezotage(request):
    if request.method == 'POST':
        form = RezotageForm(request.POST)
        if form.is_valid():
            enregisterRezotage(form, request.user)
            return redirect('page_accueil')

    else:
        form = RezotageForm()

    return render(request, "TRezotage.html", locals())

def enregisterRezotage(form, utili):
    adhr = Adherent(nom=form.cleaned_data['nom'], prenom=form.cleaned_data['prenom'], mail=form.cleaned_data['mail'], chambre=form.cleaned_data['chambre'])
    adhr.save()
    payement = Payement(credit=form.cleaned_data['payementFictif'], montantRecu=form.cleaned_data['payementRecu'], commentaire=form.cleaned_data['commentaire'])
    chaine = form.cleaned_data['sourcePayement']
    if not chaine:
        chaine = "Liquide"
    payement.banque = chaine
    payement.beneficiaire=adhr
    try:
        newUser = Utilisateur.objects.get(user=utili)
    except Utilisateur.DoesNotExist:
        newUser = Utilisateur(user=utili)
        newUser.save()
        print("Session pour un utilisateur non reconnu,création de l'entité")
    payement.rezoman = newUser
    ordi = Ordinateur(adresseMAC=form.cleaned_data['premiereMAC'], proprietaire=adhr)

    logRezotage = Log(editeur=newUser)
    logRezotage.description = "L\'adhérent {0} vient d'être créé".format(adhr)
    #try:
    ordi.save()
    payement.save()
    logRezotage.save()
    """except ConstanteNotFind, exc:
        print("{0}".format(exc))
        return"""
    print("L\'adhérent {0} va être créé avec le payement {1}, l'ordinateur {2} et le log {3}".format(adhr, payement, ordi, logRezotage))
    print("Formulaire déclaré valide")