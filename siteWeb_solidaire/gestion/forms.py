from django import forms
from .models import Payement, Log
from ressourcesAdherent.models import Adherent

#Formulaire pour la page de connexion (il est assez explicite comme ça)
class connexionForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur", max_length=30)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)


class PayementViewForm(forms.ModelForm):
    #Sous classe pour les paramètres d'affichage de l'entité
    class Meta:
        model = Payement
        fields = ['banque', 'credit', 'montantRecu', 'commentaire']

    #Fonction qui effectue la mise a jour de l'entité : copie du formulaire, enregistrement et création du Log
    def editer(self, admin, payement):
        payement.credit = self.instance.credit
        payement.banque = self.instance.banque
        payement.montantRecu = self.instance.montantRecu
        payement.commentaire = self.instance.commentaire
        payement.save()
        log = Log(editeur=admin, description="Le payement {0} à été mis à jour".format(payement))
        log.save()
