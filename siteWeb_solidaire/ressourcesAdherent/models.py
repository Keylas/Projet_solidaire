# coding=utf8

from django.db import models
from django_enumfield import enum
from django.utils import timezone
from django.core.validators import RegexValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from smtplib import SMTPException
import unicodedata
import hashlib
import hmac
import random
import string

class Chambre(models.Model):
    numero = models.CharField(max_length=4, primary_key=True, verbose_name="Numéro de la chambre")
    switch = models.CharField(max_length=2, verbose_name="Switch relie à la chambre")
    port = models.IntegerField(verbose_name="Numéro de port de la chambre")

    def __str__(self):
        return "{0}".format(self.numero)

class Adherent(models.Model):
    """Models des adhérents qui permet la gestion administrative"""
    nom = models.CharField(max_length=45, verbose_name="Nom de famille")
    prenom = models.CharField(max_length=30, verbose_name="Prénom")
    mail = models.EmailField(max_length=150, verbose_name="e-mail de contact")
    #chambre = models.CharField(max_length=4, verbose_name="Numéro de chambre", validators=[
    #    RegexValidator(regex=r'^[A-DH][0-3]((0[0-9])|(1[0-3]))$', message="Erreur: cette chambre ne peut exister")],
    #                            unique=True, null=True)
    chambre = models.OneToOneField(Chambre, verbose_name="Chambre de l'adhérent", related_name='locataire', null=True)

    dateExpiration = models.DateField(verbose_name="Date de coupure de l'adhérent",
                                      default=timezone.now().date())  # date limite avant la coupure de l'adherent
    commentaire = models.TextField(blank=True, verbose_name="Commentaire sur l'adhérent")
    estRezoman = models.BooleanField(default=False,
                                     verbose_name="statut de Rezoman")  # Si l'adhérent bénéficie du statut de Rezoman (filtrage MAC)
    estValide = models.BooleanField(default=False,
                                    verbose_name="l'adherent est valide")  # Si l'adhérent à accès aux services du rezo.

    identifiant = models.CharField(max_length=42, verbose_name="Identifiant du wifi", unique=True)
    passwordWifi = models.BinaryField(max_length=1000, verbose_name="Mot de passe pour le Wifi (encrypt0é)", default=b'')

    def __str__(self):
        """Retourne une chaîne de caractère caractéristique de l'adhérent"""
        return "{0} ".format(self.nom).upper() + "{0}".format(self.prenom).capitalize()

    def save(self, *argc, **argv):
        """Surcharge de la fonction d'enregistrement, qui s'occupe de formater les entrées préalablement"""
        # On met a jour le statut et on formate les chaînes.
        self.estValide = (self.dateExpiration >= timezone.now().date())
        self.nom = self.nom.upper()
        self.prenom = self.prenom.capitalize()
        adhr = Adherent.objects.get(pk=self.pk)
        # Controle de l'etat de la chambre pour la libérer si nécéssaire.
        if self.chambre.locataire != adhr:
            self.chambre.locataire.chambre = None
            self.chambre.locataire.save()
            # Si la chambre n'est pas vide (renseigner)
            #try:  # On verifie si la chambre est déjà assigné pour la vider dans ce cas
            #    adhr = Adherent.objects.get(chambre=self.chambre)
            #    adhr.chambre = None
            #    adhr.save()
            #except Adherent.DoesNotExist:  # Cas ou la chambre est libre
            #    pass
            self.chambre.locataire

        if(self.passwordWifi == b'' or self.passwordWifi is None or adhr is not None and self.identifiant != adhr.identifiant):
            chaine = id_generator(10)
            self.passwordWifi = create_NT_hashed_password_v2(chaine, self.identifiant, "rezo") #fout la merde avec le binaire/string
            try:
                send_mail("Mot de passe Wifi", "Bonjour,\n Ceci est votre mot de passe pour la connexion Wifi du rezo : {0}".format(chaine),
                          "rezoWifi@rez.fr", ["{0}".format(self.mail)], fail_silently=False)
            except SMTPException:
                print("Erreur lors de l'envoi du mail")

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

def id_generator(size, chars=string.ascii_uppercase + string.digits+string.ascii_lowercase):
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))

def create_NT_hashed_password_v2(passwd, user, domain):
    "create NT hashed password"
    digests = hashlib.new('md4', passwd.encode('utf-16le')).digest()
    return hmac.new(digests, (user.upper()+domain).encode('utf-16le')).digest()

class Ordinateur(models.Model):
    """Model des objets représentant les ordinateurs. Ils definissent l'IP et la MAC du PC autorisé"""

    nomDNS = models.CharField(max_length=20, primary_key=True, verbose_name="nom indice du PC")
    DNSactif = models.BooleanField(verbose_name="non DNS actif ?", default=False)
    adresseMAC = models.CharField(max_length=17, validators=[
        RegexValidator(regex=r'^([a-fA-F0-9]{2}[: ;]?){5}[a-fA-F0-9]{2}$', message="Adresse MAC invalide")],
                                  verbose_name="Adresse MAC")
    adresseIP = models.GenericIPAddressField(protocol='IpV4', verbose_name="IP dynamique", unique=True)
    proprietaire = models.ForeignKey(Adherent, verbose_name="Possesseur de l'ordinateur",
                                     related_name='listeOrdinateur')
    carteWifi = models.BooleanField(verbose_name="Carte Wifi ?", default=False)


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
        if len(self.__class__.IP_pile) == 0:  # Si la chaîne des adresse IP n'est pas crée
            self.__class__.IP_pile = self.__class__.genererListeInitiale()  # On la crée
        self.formatage()  # On formate les donnée et on enregistre en BDD
        super(Ordinateur, self).save(*argc, **argv)

    def __str__(self):
        """Retourne une chaîne de caractère caractéristique de l'adhérent"""
        return "PC {0}".format(self.nomDNS)

    def formatage(self):
        """Fonction qui s'occupe de mettre en forme les différentes chaînes de caractères avant l'enregistrement."""
        # Formatage du nom du pc, pour générer les clés primaires
        if not self.nomDNS or self.nomDNS == "":
            if len(self.proprietaire.prenom) > 3:  # On recupère les 3 premier caractère du prénom
                pren = self.proprietaire.prenom[0:3]
            else:
                pren = self.proprietaire.prenom
            chaine = self.proprietaire.nom.lower().lstrip() + pren.lower()  # On crée la chaine en la normalisant
            chaine = chaine = unicodedata.normalize('NFKD', chaine).encode('ASCII', 'ignore').decode('utf-8')
            res = Ordinateur.objects.filter(nomDNS__contains=chaine)  # On compte le nombre d'ordinateur de cet adhérent
            self.nomDNS = chaine + "{0}".format(res.count() + 1)  # et on en rajoute 1

        # Formatage de l'adresse MAC
        chtemp = self.adresseMAC.replace(' ', '')
        chtemp = chtemp.replace(':', '')
        chtemp = chtemp.replace(';', '')
        li = [chtemp[0:2], chtemp[2:4], chtemp[4:6], chtemp[6:8], chtemp[8:10], chtemp[10:12]]
        self.adresseMAC = ":".join(li)

        # Obtention de l'adresse IP
        if not self.adresseIP:
            self.adresseIP = self.__class__.IP_pile.pop()

    def delete(self, using=None):
        self.__class__.IP_pile.a
        super(Ordinateur, self.delete(using))
