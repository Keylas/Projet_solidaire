from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Adherent, Ordinateur
from gestion.models import Payement, Constante
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
            enregisterRezotage(form)
            return redirect('page_accueil')

    else:
        form = RezotageForm()

    return render(request, "TRezotage.html", locals())

def enregisterRezotage(form):
    adhr = Adherent(nom=form.cleaned_data['nom'], prenom=form.clean_data['prenom'], mail=form.cleand_data['mail'], chambre=form.cleaned_data['chambre'])
    #adhr.save()
    payement = Payement(credit=form.cleaned_data['payementFictif'], montantRecu=form.cleaned_data['payementRecu'], commentaire=form.cleaned_data['commentaire'])
    chaine = form.cleaned_data['sourcePayement']
    if not chaine:
        chaine = "Liquide"
    payement.banque = chaine
    print("Formulaire déclaré valide")