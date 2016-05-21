##Ensemble des fonctions qui génère les vues liée aux action du module ressorucesAdherent

#coding=utf8
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.forms import formset_factory
from .models import Adherent, Ordinateur, Chambre
from gestion.models import Payement, Utilisateur, Log, ConstanteNotFind
from .forms import RezotageForm, AdherentForm, MacForm, FormulaireAdherentComplet


##Vue de la liste des Adherent, surchage d'une vue générique de Django
class ListeAdherent(ListView):
    #model = Adherent
    ##variable utilisé dans le templates pour la liste des adhérents
    context_object_name = "liste_Adherent"
    ##Template utilisé par cette vue
    template_name="TAdherent.html"
    ##Nombre maximal d'Adhérent sur une page
    paginate_by = 50

    ##Permet d'imposer a toutes les fonction de cette classe de demander la connexion préalablement
    #@param self Réference vers la vue
    #@param args liste d'arguments optionnels
    #@param kwargs dictionnaire d'arguments optionnels
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ListeAdherent, self).dispatch(*args, **kwargs)

    ##Surcharge de la fonction native de django qui définit les entités selectionnée pour l'afichage
    #Prend en compte le champ de recherche pour filtrer les sorties
    #@param self Référence vers la vue
    def get_queryset(self):
        filtre = self.request.GET.get('the_search', '')
        if(filtre == ''):
            return Adherent.objects.all().order_by('nom', 'prenom')
        return Adherent.objects.filter(Q(nom__icontains=filtre) | Q(prenom__icontains=filtre)|
                                       Q(chambre__icontains=filtre)).order_by('nom', 'prenom')


##Vue de la page de rezotage, qui s'occupe de récupérer le formulaire et de demander le traitement
#@param request requête HTTP reçu par cette page
@login_required
def rezotage(request):
    if request.method == 'POST': # Si le formulaire à été remplie
        form = RezotageForm(request.POST)
        if form.is_valid(): # et qu'il est valide
            enregisterRezotage(form, request.user) #Alors on l'enregistre
            return redirect('page_accueil')
        #Si il est faux, on le renvoie avec ses erreurs (géré par django)
    else:
        form = RezotageForm() # Si c'est la première fois que l'on arrive sur cette page, on crée un formulaire vide

    return render(request, "TRezotage.html", locals())


##Fonction qui traite le formulaire et enregistre les objects
#@param form formulaire de rezotage à enregistrer
#@param utili isntance django de l'utilisateur, à utiliser pour récuperer le rezoman
def enregisterRezotage(form, utili):
    #On crée l'adhérent et on l'enregistre
    adhr = Adherent(nom=form.cleaned_data['nom'], prenom=form.cleaned_data['prenom'], mail=form.cleaned_data['mail'],
                    identifiant=form.cleaned_data['identifiantWifi'])
    try:
        chambre = Chambre.objects.get(pk=form.cleaned_data['chambre'])
    except Chambre.DoesNotExist:
        print("erreur !!!")
        return
    adhr.chambre = chambre
    adhr.save()
    #On crée le payement en verifiant la source de payement
    payement = Payement(credit=form.cleaned_data['payementFictif'], montantRecu=form.cleaned_data['payementRecu'],
                        commentaire=form.cleaned_data['commentaire'])
    chaine = form.cleaned_data['sourcePayement']
    if not chaine:
        chaine = "Liquide"
    payement.banque = chaine
    payement.beneficiaire=adhr
    #Si l'utilisateur django n'a pas de correspondance avec un rezoman (impossible en théorie), on crée la corespondance
    """try:
        newUser = Utilisateur.objects.get(user=utili)
    except Utilisateur.DoesNotExist:
        newUser = Utilisateur(user=utili)
        newUser.save()
        print("Session pour un utilisateur non reconnu,création de l'entité")"""
    newUser = Utilisateur.getUtilisateur(utili)
    payement.rezoman = newUser
    #On crée ensuite l'ordinateur et le log
    ordi = Ordinateur(adresseMAC=form.cleaned_data['premiereMAC'], proprietaire=adhr)

    logRezotage = Log(editeur=newUser)
    logRezotage.description = "L\'adhérent {0} a été créé".format(adhr)
    #et on sauvegrade le tout (il faudra gérer les erreurs ici)
    ordi.save()
    payement.save()
    logRezotage.save()
    print("L\'adhérent {0} va être créé avec le payement {1}, l'ordinateur {2} et le log {3}".format(adhr, payement, ordi, logRezotage))
    print("Formulaire déclaré valide")

##Vue de la liste des Ordinateur, surchage d'une vue générique de Django
class ListeOrdinateur(ListView):
    #model = Ordinateur
    ##Nom de la reference de la selection en BDD pour le template
    context_object_name = 'liste_Ordinateur'
    ##Nom du template utilisé pour l'affichage
    template_name = 'TOrdinateur.html'
    ##Nombre maximal d'Adhérent sur une page
    paginate_by = 50

    ##Permet d'imposer a toutes les fonction de cette classe de demander la connexion préalablement
    #@param self Réference vers la vue
    #@param args liste d'arguments optionnels
    #@param kwargs dictionnaire d'arguments optionnels
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        """Permet d'imposer a toutes les fonction de cette classe de demander la connexion préalablement"""
        return super(ListeOrdinateur, self).dispatch(*args, **kwargs)

    ##Surcharge de la fonction native de django qui définit les entités selectionnée pour l'afichage
    #Prend en compte le champ de recherche pour filtrer les sorties
    #@param self Référence vers la vue
    def get_queryset(self):
        filtre = self.request.GET.get('the_search', '')
        if(filtre == ''):
            return Ordinateur.objects.all().order_by('adresseIP')
        return Ordinateur.objects.filter(Q(proprietaire__nom__icontains=filtre) | Q(proprietaire__prenom__icontains=filtre)|
                                         Q(adresseIP__icontains=filtre)|Q(adresseMAC__icontains=filtre)).order_by('adresseIP')

##Vue qui affiche la description d'un adhérent, et permet l'édition de celui-ci
#@param request requête HTTP pour la vue
#@param adhrId Id de l'adhérent à éditer
@login_required
def editionA(request, adhrId):
    adhr = get_object_or_404(Adherent, pk=adhrId)
    localId = adhrId

    form = FormulaireAdherentComplet(adhr, request.POST)
    if form.is_valid():
        form.save(Utilisateur.getUtilisateur(request.user))
        return redirect('affichageAdherent')

    listeZip = zip(form.listeForm, form.adherent.listeOrdinateur.all())
    lastForm = form.listeForm[-1]
    return render(request, "TEditionAdherent.html", locals())

##Vue qui s'occupe de la supréssion d'un ordinateur
#@param request requête HTTP pour la vue
#@param ordiPk ID de l'ordinateur à supprimer
@login_required
def supressionOrdinateur(request, ordiPk):
    ordi = get_object_or_404(Ordinateur, pk=ordiPk)
    ordi.delete()
    return redirect('affichageOrdinateur')