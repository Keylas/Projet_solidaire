from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Adherent, Ordinateur
from gestion.models import Payement, Utilisateur, Log, ConstanteNotFind
from .forms import RezotageForm

# Create your views here.

class ListeAdherent(ListView):
    """Vue de l'entité adherent représente par une classe générique de django"""
    model = Adherent
    context_object_name = "liste_Adherent" # variable utilisé dans le templates pour la liste des adhérents
    template_name="TAdherent.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        """Permet d'imposer a toutes les fonction de cette classe de demander la connexion préalablement"""
        return super(ListeAdherent, self).dispatch(*args, **kwargs)

@login_required
def rezotage(request):
    """Vue du rezotage, qui s'occupe de récupérer le formulaire"""
    if request.method == 'POST': # Si le formulaire à été remplie
        form = RezotageForm(request.POST)
        if form.is_valid(): # et qu'il est valide
            enregisterRezotage(form, request.user) #Alors on l'enregistre
            return redirect('page_accueil')
        #Si il est faux, on le renvoie avec ses erreurs (géré par django)
    else:
        form = RezotageForm() # Si c'est la première fois que l'on arrive sur cette page, on crée un formulaire vide

    return render(request, "TRezotage.html", locals())

def enregisterRezotage(form, utili):
    """Fonction qui traite le formulaire et enregistre les objects"""
    #On crée l'adhérent et on l'enregistre
    adhr = Adherent(nom=form.cleaned_data['nom'], prenom=form.cleaned_data['prenom'], mail=form.cleaned_data['mail'], chambre=form.cleaned_data['chambre'])
    adhr.save()
    #On crée le payement en verifiant la source de payement
    payement = Payement(credit=form.cleaned_data['payementFictif'], montantRecu=form.cleaned_data['payementRecu'], commentaire=form.cleaned_data['commentaire'])
    chaine = form.cleaned_data['sourcePayement']
    if not chaine:
        chaine = "Liquide"
    payement.banque = chaine
    payement.beneficiaire=adhr
    #Si l'utilisateur django n'a pas de correspondance avec un rezoman (impossible en théorie), on crée la corespondance
    try:
        newUser = Utilisateur.objects.get(user=utili)
    except Utilisateur.DoesNotExist:
        newUser = Utilisateur(user=utili)
        newUser.save()
        print("Session pour un utilisateur non reconnu,création de l'entité")
    payement.rezoman = newUser
    #On crée ensuite l'ordinateur et le log
    ordi = Ordinateur(adresseMAC=form.cleaned_data['premiereMAC'], proprietaire=adhr)

    logRezotage = Log(editeur=newUser)
    logRezotage.description = "L\'adhérent {0} vient d'être créé".format(adhr)
    #et on sauvegrade le tout (il faudra gérer les erreurs des constantes ici)
    #try:
    ordi.save()
    payement.save()
    logRezotage.save()
    """except ConstanteNotFind, exc:
        print("{0}".format(exc))
        return"""
    print("L\'adhérent {0} va être créé avec le payement {1}, l'ordinateur {2} et le log {3}".format(adhr, payement, ordi, logRezotage))
    print("Formulaire déclaré valide")