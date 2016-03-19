from django import forms
import re
from .models import Adherent, Ordinateur
from gestion.models import Log


class RezotageForm(forms.Form):
    nom = forms.CharField(label="Nom")
    prenom = forms.CharField(label="Prénom")
    mail = forms.EmailField(label="E-mail de contact")

    # rezoman = forms.BooleanField(label="Rezoman", required=False)
    chambre = forms.CharField(label="Chambre", max_length=4)
    premiereMAC = forms.CharField(label="MAC principale", max_length=17)

    payementRecu = forms.DecimalField(label="Montant Réel", min_value=0.0, decimal_places=2)
    payementFictif = forms.DecimalField(label="Crédit de l'adhérent", min_value=0.0, decimal_places=2)
    sourcePayement = forms.CharField(label="Banque (laisser vide si espèce)", required=False)
    commentaire = forms.CharField(label="Commentaire (obligatoire si les deux montants sont différents)",
                                  widget=forms.Textarea, required=False)

    def clean_premiereMAC(self):
        mac = self.cleaned_data['premiereMAC']
        if re.search(r'^([a-fA-F0-9]{2}[: ;]?){5}[a-fA-F0-9]{2}$', mac) is None:
            raise forms.ValidationError("Adresse MAC invalide")

        return mac

    def clean_chambre(self):
        chambre = self.cleaned_data['chambre']
        if re.search(r'^[A-DH][0-3]((0[0-9])|(1[0-3]))$', chambre) is None:
            raise forms.ValidationError("Cette chambre n'existe pas")

        return chambre

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


class AdherentForm(forms.Form):
    nom = forms.CharField(label="Nom")
    prenom = forms.CharField(label="Prénom")
    mail = forms.EmailField(label="E-mail de contact")

    rezoman = forms.BooleanField(label="Rezoman", required=False)
    chambre = forms.CharField(label="Chambre", max_length=4)
    identifiant = forms.CharField(label="identifiant Wifi", max_length=42)

    def clean_chambre(self):
        chambre = self.cleaned_data['chambre']
        if re.search(r'^[A-DH][0-3]((0[0-9])|(1[0-3]))$', chambre) is None:
            raise forms.ValidationError("Cette chambre n'existe pas")

        return chambre


class MacForm(forms.Form):
    adresseMAC = forms.CharField(label="adresse MAC", max_length=17)
    carteWifi = forms.BooleanField(label="Carte Wifi ?", required=False)

    def clean_adresseMAC(self):
        mac = self.cleaned_data['adresseMAC']
        # print("On controle bien l'adresse MAC")
        if re.search(r'^([a-fA-F0-9]{2}[: ;]?){5}[a-fA-F0-9]{2}$', mac) is None:
            raise forms.ValidationError("Adresse MAC invalide")

        return mac


class FormulaireAdherentComplet():
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

    def save(self, admin):
        modif = False
        if self.mainForm.has_changed():
            # print(', '.join(self.mainForm.changed_data))
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
