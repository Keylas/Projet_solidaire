from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Log, Payement, Utilisateur
from .forms import PayementViewForm
from ressourcesAdherent.models import Adherent


#Classe qui génère la vue d'affichage des logs avec le template de l'accueil
class ListeLog(ListView):
    model = Log
    context_object_name = "liste_Log"
    template_name = "accueil.html"

    #Fonction qui sert a demander une session pour accéder au pages de la classe
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ListeLog, self).dispatch(*args, **kwargs)

#Classe qui génère la vue d'affichage des différents payements.
class ListePayement(ListView):
    model = Payement
    context_object_name = "liste_Payement"
    template_name = "TPayement.html"
    ordering = ['dateCreation']

    #Fonction qui sert a demander une session pour accéder au pages de la classe
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ListePayement, self).dispatch(*args, **kwargs)


#vue pour l'édition d'un payement défini par Id
@login_required
def editerPayement(request, id):
    #On tente de récupérer le payement, et on envoie une page 404 si l'id du payement n'existe pas
    payement = get_object_or_404(Payement, pk=id)

    localId = id #On sauvegarde l'id en local pour l'envoyer au template
    if request.method == 'POST': #Si on a reçu la réponse du formulaire
        form = PayementViewForm(request.POST)
        if form.is_valid(): #On vérifie que le formulaire est valide, dans le cas contraire on renvoie la page
            form.editer(Utilisateur.getUtilisateur(request.user), payement) #On édite le payement
            return redirect('page_payement') #et on retourne si la page de la liste des payements
    else:
        form = PayementViewForm(instance=payement) #Si c'est le premier appel de cette page, on envoie le formulaire préremplie avec le payement voulu

    #On génère la page ensuite
    return render(request, 'TEditionPayement.html', locals())


#Vue pour la création du payement, très simillaire a la vue précédente
@login_required
def creerPayement(request, adhrId):
    #On récupère les variables locales
    adhr = get_object_or_404(Adherent, pk=adhrId)

    localId = adhrId
    #Si on a reçu un formulaire
    if request.method == 'POST':
        form = PayementViewForm(request.POST)
        if form.is_valid(): #On vérifie s'il est valide
            #Dans ce cas, on crée le payement
            form.instance.beneficiaire = adhr
            form.instance.rezoman = Utilisateur.getUtilisateur(request.user)
            form.save()
            return redirect('affichageAdherent') #et on retourne sur la page des adhérent
    else:
        form = PayementViewForm() #Sinon on envoie un formulaire vide pour créer le payement

    #Et on génère la page
    return render(request, 'TCreationPayement.html', locals())

class ListeUtilisateur(ListView):
    model = Utilisateur
    context_object_name = "liste_utilisateur"
    template_name = "TUtilisateur.html"

    #Fonction qui sert a demander une session pour accéder au pages de la classe
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ListeUtilisateur, self).dispatch(*args, **kwargs)