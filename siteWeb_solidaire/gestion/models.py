# coding=utf8

from django.db import models
from django_enumfield import enum
from django.contrib.auth.models import User, Group
from ressourcesAdherent.models import Adherent
from Script.ScriptsCoupure import modifAdherent
from django.core.exceptions import ValidationError
from datetime import datetime, date, timedelta


class ConstanteNotFind(Exception):
    def __init__(self, raison):
        self.raison = raison

    def __str__(self):
        return self.raison


class RoleRezoman(enum.Enum):
    """Enumeration pour les statuts des utilisateurs du site"""
    MEMBRE = 0
    PREZ = 1
    TREZ = 2
    SCREZ = 3
    SUPERMEMBRE = 4

    labels = {
        MEMBRE: "Membre",
        PREZ: "Président",
        TREZ: "Trésorier",
        SCREZ: "Secrétaire",
        SUPERMEMBRE: "Membre avec plus de pouvoir",
    }

    def __str__(self):
        return reverse(self)

    def reverse(x):
        return {
            1: "Président",
            2: "Trésorier",
            3: "Secrétaire",
            4: "Membre avec des supers pouvoirs",
        }.get(x, "Membre actif")

    @classmethod
    def genererTuples(cls):
        return ((0, "Membre"), (1, "Président"), (2, "Trésorier"), (3, "Secretaire"))


class EtatPayement(enum.Enum):
    """Enumeration des etats d'un payement"""
    DECLARE = 0
    RECEPTIONNE = 1
    ENCAISSE = 2

    def __str__(self):
        if self == EtatPayement.ENCAISSE:
            return "encaissé à la banque"
        elif self == EtatPayement.RECEPTIONNE:
            return "récéptionné par la trésorerie"
        else:
            return "déclaré par un rezoman"

    # Défini les conditions de chamgement d'un etat à l'autre
    _transitions = {
        ENCAISSE: (RECEPTIONNE,),
        RECEPTIONNE: (DECLARE,)
    }


class Utilisateur(models.Model):
    """Entité qui représente un modérateur du site"""
    user = models.OneToOneField(User, verbose_name="identifiants de connexion")
    role = enum.EnumField(RoleRezoman, default=RoleRezoman.MEMBRE, verbose_name="statut du rezoman")

    def __str__(self):
        return "{0}, {1}".format(self.user.username, RoleRezoman.reverse(self.role))

    @classmethod
    def getUtilisateur(cls, utili):
        try:
            newUser = cls.objects.get(user=utili)
        except cls.DoesNotExist:
            newUser = cls(user=utili)
            newUser.save()
            print("Session pour un utilisateur non reconnu,création de l'entité")
        return newUser

    def parseRole(self):
        return RoleRezoman.reverse(self.role)

    def save(self, *args, **kwargs):
        #Gerer le changement de status (detection des roles ne marche pas, recuperation des groupes ??)
        #print(self.role)
        #print(RoleRezoman.MEMBRE)
        if self.role == str(RoleRezoman.MEMBRE):
            print("Membre")
            self.user.groups = [Group.objects.get(name="Membre")]

        else:
            print("Bureau")
            self.user.groups = [Group.objects.get(name="MembreBureau")]

        self.user.save()
        super(Utilisateur, self).save(*args, **kwargs)

class Log(models.Model):
    """Entité des logs des activités des modérateurs"""
    class Meta:
        ordering = ['-date'] # Defini la methode de classement

    date = models.DateTimeField(auto_now_add=True, auto_now=False)
    description = models.TextField(null=False)
    editeur = models.ForeignKey(Utilisateur, related_name='listeLog')

    def __str__(self):
        """Renvoie une chaine de caractère représentative de l'entité"""
        return "Log du {0} exécuté par {2} : {1}".format(self.date.date(), self.description, self.editeur)


class Payement(models.Model):
    """Entité qui représente les payements"""
    class Meta:
        ordering = ['-dateCreation']

    beneficiaire = models.ForeignKey(Adherent, verbose_name="Membre créditeur", related_name='listePayement')
    rezoman = models.ForeignKey(Utilisateur, verbose_name="Rezoman créateur du payement", related_name='listePayement')
    dateCreation = models.DateField(auto_now_add=True, editable=False)
    credit = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Montant à créditer")
    montantRecu = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Montant réel payé")
    commentaire = models.TextField(blank=True,
                                verbose_name="Commentaire du créateur, à remplir si les deux montants sont différents")
    banque = models.CharField(blank=True, max_length=42)
    etat = enum.EnumField(EtatPayement, default=EtatPayement.DECLARE)

    def __str__(self):
        """Renvoie une chaine de caractère représentative de l'entité"""
        return "Payement de {0} euros à compter du {1}".format(self.credit, str(self.dateCreation))

    def clean(self):
        super(Payement, self).clean()
        if self.montantRecu != self.credit and not self.commentaire:
            raise ValidationError({'commentaire': "Il faut justifier pourquoi les montants sont différents !"})

    def save(self, *args, **kwargs):
        """Surcharge de la fonction d'enregistrement afin de mettre a jour l'adherent concerné"""
        # On tente de recupérer les constantes de conversion prix->temps
        try:
            cste1 = Constante.objects.get(cle="PRIX_MENSUEL")
            cste2 = Constante.objects.get(cle="DUREE_MOIS")
        except Constante.DoesNotExist:
            # Si une des constantes n'est pas disponible, il faut générer une erreur (non traité)
            print("ERREUR : les constantes ne sont pas recupérable")
            raise ConstanteNotFind("Les constantes ne sont pas accessible")

        #On verifie si le payement est par chèques ou en liquide
        if self.banque is None or self.banque == '' or self.banque == "":
            self.banque = "Liquide"
        # On verifie si le payement existe deja, dans ce cas c'est une modification
        try:
            payementAnt = Payement.objects.get(pk=self.pk) # On récupère l'ancien payement
            jour = int((self.credit-payementAnt.credit) * cste2.value / cste1.value) # Et on calcule la variation de jours
        except Payement.DoesNotExist:
            jour = int(self.credit * cste2.value / cste1.value) # Sinon c'est un nouveau payement

        super(Payement, self).save(args, kwargs)  # On sauvegrade en BDD
        if self.beneficiaire.estValide:
            self.beneficiaire.dateExpiration = self.beneficiaire.dateExpiration + timedelta(days=jour)# On ajoute le crédit
        else:
            self.beneficiaire.dateExpiration = datetime.now().date() + timedelta(days=jour)# Ou on initialise le crédit
        self.beneficiaire.save() # et on met à jour l'adhérent
        modifAdherent(self.beneficiaire.pk)


class Constante(models.Model):
    """classe qui va contenir les differente constantes utiles pour le fonctionnement, pour le moment que des décimal"""
    cle = models.CharField(verbose_name="Nom de la constante", primary_key=True, max_length=90)
    value = models.DecimalField(verbose_name="Valeur", max_digits=20, decimal_places=10)

    def __str__(self):
        return self.cle