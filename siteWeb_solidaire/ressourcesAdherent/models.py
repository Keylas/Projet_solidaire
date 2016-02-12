# coding=utf8

from django.db import models
from django_enumfield import enum
from django.utils import timezone
from django.core.validators import RegexValidator, MinValueValidator
import unicodedata


class Adherent(models.Model):
    """Models des adhérents qui permet la gestion administrative"""
    nom = models.CharField(max_length=45, verbose_name="Nom de famille")
    prenom = models.CharField(max_length=30, verbose_name="Prénom")
    mail = models.EmailField(max_length=150, verbose_name="e-mail de contact")
    chambre = models.CharField(max_length=4, verbose_name="Numéro de chambre", validators=[
        RegexValidator(regex=r'^[A-DH][0-3]((0[0-9])|(1[0-3]))$', message="Erreur: cette chambre ne peut exister")],
                               unique=True, null=True)
    dateExpiration = models.DateField(verbose_name="Date de coupure de l'adhérent",
                                      default=timezone.now)  # date limite avant la coupure de l'adherent
    commentaire = models.TextField(blank=True, verbose_name="Commentaire sur l'adhérent")
    estRezoman = models.BooleanField(default=False,
                                     verbose_name="statut de Rezoman")  # Si l'adhérent bénéficie du statut de Rezoman (filtrage MAC)
    estValide = models.BooleanField(default=False,
                                    verbose_name="l'adherent est valide")  # Si l'adhérent à accès aux services du rezo.

    def __str__(self):
        """Retourne une chaîne de caractère caractéristique de l'adhérent"""
        return "{0} ".format(self.nom).upper() + "{0}".format(self.prenom).capitalize()

    def save(self, *argc, **argv):
        """Surcharge de la fonction d'enregistrement, qui s'occupe de formater les entrées préalablement"""
        # On met a jour le statut et on formate les chaînes.
        self.estValide = (self.dateExpiration.date() >= timezone.now().date())
        self.nom = self.nom.upper()
        self.prenom = self.prenom.capitalize()

        # Controle de l'etat de la chambre pour la libérer si nécéssaire.
        if self.chambre:  # Si la chambre n'est pas vide (renseigner)
            try:  # On verifie si la chambre est déjà assigné pour la vider dans ce cas
                adhr = Adherent.objects.get(chambre=self.chambre)
                adhr.chambre = None
                adhr.save()
            except Adherent.DoesNotExist:  # Cas ou la chambre est libre
                pass

        # On finit les controles puis on sauvegarde.
        try:
            super(Adherent, self).validate_unique()
            super(Adherent, self).save(*argc, **argv)
        except ValidationError:
            pass

    def validate_unique(self, exclude=None):
        """Surcharge de la fonction originelle afin de ne pas controler ici l'unicité de la chambre"""
        exclude.append('chambre')  # On ajoute la chambre au champs dont on ne verifie pas l'unicité.
        super(Adherent, self).validate_unique(exclude)


class Ordinateur(models.Model):
    """Model des objets représentant les ordinateurs. Ils definissent l'IP et la MAC du PC autorisé"""

    nomDNS = models.CharField(max_length=20, primary_key=True, verbose_name="nom indice du PC")
    adresseMAC = models.CharField(max_length=17, validators=[
        RegexValidator(regex=r'^([a-fA-F0-9]{2}[: ;]?){5}[a-fA-F0-9]{2}$', message="Adresse MAC invalide")],
                                  verbose_name="Adresse MAC")
    adresseIP = models.GenericIPAddressField(protocol='IpV4', verbose_name="IP dynamique", unique=True)
    proprietaire = models.ForeignKey(Adherent, verbose_name="Possesseur de l'ordinateur",
                                     related_name='listeOrdinateur')

    @classmethod
    def genererListeInitiale(cls, taille=1024):
        """Préremplie la liste des IP disponible en fonction de celle en BDD"""
        pile = []
        for i in range(taille, -1, -1):
            ipChaine = "10.2."
            ipChaine += "{0}.{1}".format((i // 256) + 1, i % 256)
            try:
                Ordinateur.objects.get(adresseIP=ipChaine)
            except Ordinateur.DoesNotExist:
                pile.append(ipChaine)

        return pile

    IP_pile = []  # Pile qui va contenir les IP disponible.

    def save(self, *argc, **argv):
        """Surcharge de la fonction de sauvegarde qui va s'occuper de formater les chaînes préalablement"""
        if len(self.__class__.IP_pile) == 0:
            self.__class__.IP_pile = self.__class__.genererListeInitiale()
        self.formatage()
        super(Ordinateur, self).save(*argc, **argv)

    def __str__(self):
        """Retourne une chaîne de caractère caractéristique de l'adhérent"""
        return "PC {0}".format(self.nomDNS)

    def formatage(self):
        """Fonction qui s'occupe de mettre en forme les différentes chaînes de caractères avant l'enregistrement."""
        # Formatage du nom du pc, pour générer les clés primaires
        if not self.nomDNS or self.nomDNS == "":
            if len(self.proprietaire.prenom) > 3:
                pren = self.proprietaire.prenom[0:3]
            else:
                pren = self.proprietaire.prenom
            chaine = self.proprietaire.nom.lower().lstrip() + pren.lower()
            chaine = chaine = unicodedata.normalize('NFKD', chaine).encode('ASCII', 'ignore').decode('utf-8')
            res = Ordinateur.objects.filter(nomDNS__contains=chaine)
            self.nomDNS = chaine + "{0}".format(res.count() + 1)

        # Formatage de l'adresse MAC
        chtemp = self.adresseMAC.replace(' ', '')
        chtemp = chtemp.replace(':', '')
        chtemp = chtemp.replace(';', '')
        li = [chtemp[0:2], chtemp[2:4], chtemp[4:6], chtemp[6:8], chtemp[8:10], chtemp[10:12]]
        self.adresseMAC = ":".join(li)

        # Obtention de l'adresse IP
        if not self.adresseIP:
            self.adresseIP = self.__class__.IP_pile.pop()
