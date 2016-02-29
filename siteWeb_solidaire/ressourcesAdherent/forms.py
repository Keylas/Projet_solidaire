from django import forms
import re
from .models import Adherent, Ordinateur

class RezotageForm(forms.Form):
    nom = forms.CharField(label="Nom")
    prenom = forms.CharField(label="Prénom")
    mail = forms.EmailField(label="E-mail de contact")

    #rezoman = forms.BooleanField(label="Rezoman", required=False)
    chambre = forms.CharField(label="Chambre", max_length=4)
    premiereMAC = forms.CharField(label="MAC principale", max_length=17)

    payementRecu = forms.DecimalField(label="Montant Réel", min_value=0.0, decimal_places=2)
    payementFictif = forms.DecimalField(label="Crédit de l'adhérent", min_value=0.0, decimal_places=2)
    sourcePayement = forms.CharField(label="Banque (laisser vide si espèce)", required=False)
    commentaire = forms.CharField(label="Commentaire (obligatoire si les deux montants sont différents)", widget=forms.Textarea, required=False)

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

    def clean_chambre(self):
        chambre = self.cleaned_data['chambre']
        if re.search(r'^[A-DH][0-3]((0[0-9])|(1[0-3]))$', chambre) is None:
            raise forms.ValidationError("Cette chambre n'existe pas")

        return chambre

class MacForm(forms.Form):
    adresseMAC = forms.CharField(label="adresse MAC", max_length=17)

    def clean_adresseMAC(self):
        mac = self.cleaned_data['adresseMAC']
        print("On controle bien l'adresse MAC")
        if re.search(r'^([a-fA-F0-9]{2}[: ;]?){5}[a-fA-F0-9]{2}$', mac) is None:
            raise forms.ValidationError("Adresse MAC invalide")

        return mac