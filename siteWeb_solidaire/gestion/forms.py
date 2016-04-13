from django import forms
from .models import Payement, Log, User, Utilisateur, RoleRezoman
from django.contrib.auth.models import Group
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

class UtilisateurForm(forms.Form):
    username = forms.CharField(label="Pseudonyme", widget=forms.TextInput(attrs={'required': 'true'}))
    password1 = forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={'required': 'true'}))
    password2 = forms.CharField(label="Retapez le mot de passe", widget=forms.PasswordInput(attrs={'required': 'true'}))
    role = forms.ChoiceField(label="Role du rezoman", choices=RoleRezoman.genererTuples())

    def clean(self):
        cleaned_data = super(UtilisateurForm, self).clean()
        password = self.cleaned_data.get('password1')
        passwordConfirm = self.cleaned_data.get('password2')

        if password != passwordConfirm:
            self.add_error('password2', "Password incorrect")

        return cleaned_data

    def save(self):
        user = User.objects.create_user(self.cleaned_data['username'], "", self.cleaned_data['password1'])
        utili = Utilisateur(user=user, role=self.cleaned_data['role'])
        utili.user.save()
        utili.save()

class UtilisateurEditionForm(forms.Form):
    username = forms.CharField(label="Pseudonyme", widget=forms.TextInput(attrs={'required': 'true'}))
    password1 = forms.CharField(label="Changement de mot de passe", widget=forms.PasswordInput(), required=False)
    password2 = forms.CharField(label="Retapez le mot de passe", widget=forms.PasswordInput(), required=False)
    role = forms.ChoiceField(label="Role du rezoman", choices=RoleRezoman.genererTuples())

    email = forms.EmailField(label="Mail", required=False)
    nom = forms.CharField(label="Nom du rezoman", required=False)
    prenom = forms.CharField(label="Prenom", required=False)

    def __init__(self, utilisateur, requestPost=None):
        self.utili = utilisateur
        self.dicInit = {'username': utilisateur.user.username, 'role': utilisateur.role, 'email': utilisateur.user.email,
                   'nom': utilisateur.user.last_name, 'prenom': utilisateur.user.first_name}
        if requestPost:
            super(UtilisateurEditionForm, self).__init__(requestPost, initial=self.dicInit)
        else:
            super(UtilisateurEditionForm, self).__init__(initial=self.dicInit)

    def clean(self):
        cleaned_data = super(UtilisateurEditionForm, self).clean()
        password = self.cleaned_data.get('password1')
        passwordConfirm = self.cleaned_data.get('password2')

        if password != passwordConfirm:
            self.add_error('password2', "Password incorrect")

        return cleaned_data

    def editer(self, admin):
        if self.has_changed():
            log = Log(editeur=admin, description="Le rezoman {0} à été mis à jour".format(self.utili))
            self.utili.user.username = self.cleaned_data['username']
            self.utili.user.email = self.cleaned_data['email']
            self.utili.user.first_name = self.cleaned_data['prenom']
            self.utili.user.last_name = self.cleaned_data['nom']
            self.utili.role = self.cleaned_data['role']

            if self.cleaned_data['password1'] != "":
                #Mettre a joue le mot de passe !
                print("On change le password !!")
                print(self.cleaned_data['password1'])

            self.utili.user.save()
            self.utili.save()
