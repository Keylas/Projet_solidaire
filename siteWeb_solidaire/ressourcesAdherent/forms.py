from django import forms
import re

class RezotageForm(forms.Form):
    nom = forms.CharField(label="Nom")
    prenom = forms.CharField(label="Prénom")
    mail = forms.EmailField(label="E-mail de contact")

    rezoman = forms.BooleanField(label="Rezoman", required=False)
    chambre = forms.CharField(label="Chambre", max_length=4)
    premiereMAC = forms.CharField(label="MAC principale", max_length=17)

    payementReçu = forms.DecimalField(label="Montant Réel", max_digits=2, min_value=0)
    payementFictif = forms.DecimalField(label="Crédit de l'adhérent", max_digits=2, min_value=0)
    sourcePayement = forms.CharField(label="Banque (laisser vide si espèce)", required=False)

    def clean_premiereMAC(self):
        mac=self.cleaned_data['premiereMAC']
        if re.search(r'^([a-fA-F0-9]{2}[: ;]?){5}[a-fA-F0-9]{2}$', mac) is None:
            raise forms.ValidationError("Adresse MAC invalide")

        return mac

    def clean_chambre(self):
        chambre=self.cleaned_data['chambre']
        if re.search(r'^[A-DH][0-3]((0[0-9])|(1[0-3]))$', chambre) is None:
            raise forms.ValidationError("Cette chambre n'existe pas")

        return chambre
