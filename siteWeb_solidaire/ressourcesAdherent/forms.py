##Fichier regroupant les formulaires utilisé par le module ressourcesAdherent pour le site (édition ou création d'entités)

# coding=utf8
from django import forms
import re
from .models import Adherent, Ordinateur
from gestion.models import Log

##Formulaire pour le rezotage d'un nouvel Adhérent
class RezotageForm(forms.Form):
    ##Champ pour le nom de l'adhérent
    nom = forms.CharField(label="Nom")
    ##Champ pour le prénom de l'adhérent
    prenom = forms.CharField(label="Prénom")
    ##Champ pour le mail de l'adhérent
    mail = forms.EmailField(label="E-mail de contact")
    ##Champ pour le numéro de la chambre de l'adhérent
    chambre = forms.CharField(label="Chambre", max_length=4)
    #Champ pour l'identifiant Wifi de l'adhérent, à utiliser pour ce connexter au futur module Wifi
    identifiantWifi = forms.CharField(max_length=42, label="ID pour le Wifi de la rez")
    ##Champ pour l'adresse MAC du premier ordinateur autorisé de l'adhérent
    premiereMAC = forms.CharField(label="MAC principale", max_length=17)
    ##Champ pour indiquer le montant que l'adhérent a payé lors du rezotage
    payementRecu = forms.DecimalField(label="Montant Réel", min_value=0.0, decimal_places=2)
    ##Champ pour le crédit à ajouter au début
    payementFictif = forms.DecimalField(label="Crédit de l'adhérent", min_value=0.0, decimal_places=2)
    ##Champ pour indiquer le type de payement
    sourcePayement = forms.CharField(label="Banque (laisser vide si espèce)", required=False)
    ##Champ pour laisser un commentaire à propos du payement
    commentaire = forms.CharField(label="Commentaire (obligatoire si les deux montants sont différents)",
                                  widget=forms.Textarea, required=False)

    ##Surcharge de la fonction native de django pour controler la validité de l'adresse MAC
    #@param self Réference vers le formulaire
    def clean_premiereMAC(self):
        mac = self.cleaned_data['premiereMAC']
        if re.search(r'^([a-fA-F0-9]{2}[: ;]?){5}[a-fA-F0-9]{2}$', mac) is None:
            raise forms.ValidationError("Adresse MAC invalide")

        return mac

    ##Surcharge de la fonction native de django pour controler la validité du numéro de chambre
    #@param self Réference vers le formulaire
    def clean_chambre(self):
        chambre = self.cleaned_data['chambre']
        if re.search(r'^[A-DH][0-3]((0[0-9])|(1[0-3]))$', chambre) is None:
            raise forms.ValidationError("Cette chambre n'existe pas")

        return chambre

    ##Surcharge de la fonction native de django pour verifier si le payement est correct (commenté si les montant reçu et crédité diffère)
    #@param self Référence vers le formulaire
    def clean(self):
        cleaned_data = super(RezotageForm, self).clean()
        fictif = cleaned_data.get('payementFictif')
        reel = cleaned_data.get('payementRecu')
        comment = cleaned_data.get('commentaire')

        if fictif and reel:
            if fictif != reel and not comment:
                msg = "Un commentaire est obligatoire si les deux montants sont différents"
                self.add_error('commentaire', msg)
            if fictif == 0.0:
                msg = "Un rezotage nécessite un crédit initial"
                self.add_error('payementFictif', msg)
        return cleaned_data


##Formulaire pour l'édition d'un adhérent, contient les information basiques.
class AdherentForm(forms.Form):
    ##Champ pour le nom de l'adhérent
    nom = forms.CharField(label="Nom")
    ##Champ pour le prénom de l'adhérent
    prenom = forms.CharField(label="Prénom")
    ##Champ pour le mail de l'adhérent
    mail = forms.EmailField(label="E-mail de contact")
    ##Champ qui permet d'indiquer si l'adhérent a les privilèges de rezoman (filtrage MAC desactivé)
    rezoman = forms.BooleanField(label="Rezoman", required=False)
    ##Champ pour le numéro de la chambre de l'adhérent
    chambre = forms.CharField(label="Chambre", max_length=4)
    #Champ pour l'identifiant Wifi de l'adhérent, à utiliser pour ce connexter au futur module Wifi
    identifiant = forms.CharField(label="identifiant Wifi", max_length=42)

    ##Surcharge de la fonction native de django pour controler la validité du numéro de chambre
    #@param self Réference vers le formulaire
    def clean_chambre(self):
        chambre = self.cleaned_data['chambre']
        if re.search(r'^[A-DH][0-3]((0[0-9])|(1[0-3]))$', chambre) is None:
            raise forms.ValidationError("Cette chambre n'existe pas")

        return chambre

##Formulaire pour l'édition d'un adhérent, partie liée aux cartes réseaux authorisées
class MacForm(forms.Form):
    ##Champs pour l'adresse MAC de la carte
    adresseMAC = forms.CharField(label="adresse MAC", max_length=17)
    #Champ pour indiquer si la carte est une carte WiFi
    carteWifi = forms.BooleanField(label="Carte Wifi ?", required=False)

    ##Surcharge de la fonction native de django pour controler la validité de l'adresse MAC
    #@param self Réference vers le formulaire
    def clean_adresseMAC(self):
        mac = self.cleaned_data['adresseMAC']
        # print("On controle bien l'adresse MAC")
        if re.search(r'^([a-fA-F0-9]{2}[: ;]?){5}[a-fA-F0-9]{2}$', mac) is None:
            raise forms.ValidationError("Adresse MAC invalide")

        return mac


##Formulaire complet pour l'édition des adhérents, regroupe les formulaire AdherentForm et MacForm
class FormulaireAdherentComplet():
    ##Constructeur du formulaire, qui génères les autres formulaires
    #@param self Reférence vers le formulaire
    #@param adherent instance de l'adhérent à éditer
    #@param POSTrequest instance de la requête POST renvoyé par ce formulaire, pour contrôler le formulaire
    def __init__(self, adherent, POSTrequest=None):
        self.adherent = adherent
        dicInit = {'nom': self.adherent.nom, 'prenom': self.adherent.prenom, 'mail': self.adherent.mail,
                   'chambre': self.adherent.chambre, 'rezoman': self.adherent.estRezoman,
                   'identifiant': self.adherent.identifiant}
        data = []
        for ordi in self.adherent.listeOrdinateur.all():
            data.append({'adresseMAC': ordi.adresseMAC, 'carteWifi': ordi.carteWifi})

        if POSTrequest:
            self.mainForm = AdherentForm(POSTrequest, initial=dicInit)
            formset = forms.formset_factory(MacForm, extra=0)
            data.append({'adresseMAC': '', 'carteWifi': False})
            self.listeForm = formset(POSTrequest, initial=data)
        else:
            self.mainForm = AdherentForm(initial=dicInit)
            formset = forms.formset_factory(MacForm, extra=1)
            self.listeForm = formset(initial=data)

        for ordiA, ordiF in zip(self.adherent.listeOrdinateur.all(), self.listeForm):
            ordiF.fields['adresseMAC'].label = "Ordinateur {0}".format(ordiA.nomDNS)
        self.listeForm[-1].fields['adresseMAC'].label = "Nouvelle MAC (laisser vide si pas de nouvelle MAC)"

    ##Surcharge de la fonction native de django qui contrôle la validité des champs du formulaire
    #@param self Réfecenre vers le formulaire
    def is_valid(self):
        valide = True
        if not self.mainForm.is_valid():
            valide = False
            print(str(self.mainForm.errors))
        for forms in self.listeForm:
            if not forms.is_valid():
                valide = False
                print(str(forms.errors))

        return valide

    ##Fonction qui enregistre les modifications de l'adhérent et crée le Log associé
    #@param self Référence vers le formulaire
    #@param admin Administrateur qui effectue l'édition
    def save(self, admin):
        modif = False
        if self.mainForm.has_changed():
            # print(', '.join(self.mainForm.changed_dat0a))
            modif = True
            self.adherent.nom = self.mainForm.cleaned_data['nom']
            self.adherent.prenom = self.mainForm.cleaned_data['prenom']
            self.adherent.mail = self.mainForm.cleaned_data['mail']
            self.adherent.chambre = self.mainForm.cleaned_data['chambre']
            self.adherent.estRezoman = self.mainForm.cleaned_data['rezoman']
            self.adherent.identifiant = self.mainForm.cleaned_data['identifiant']
            self.adherent.save()  # Exception de validation à gérer ici

        for ordiA, ordiF in zip(self.adherent.listeOrdinateur.all(), self.listeForm):
            if ordiF.has_changed():
                ordiA.adresseMAC = ordiF.cleaned_data['adresseMAC']
                ordiA.carteWifi = ordiF.cleaned_data['carteWifi']
                ordiA.save()
                modif = True

        if self.listeForm[-1].has_changed():
            modif = True
            newPC = Ordinateur(proprietaire=self.adherent, adresseMAC=self.listeForm[-1].cleaned_data['adresseMAC'],
                               carteWifi=self.listeForm[-1].cleaned_data['carteWifi'])
            newPC.save()

        if modif:
            log = Log(editeur=admin, description="L'adhérent {0} à été mis à jour".format(self.adherent))
            log.save()
            print(log)
