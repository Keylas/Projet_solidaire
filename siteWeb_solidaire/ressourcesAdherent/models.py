##Fichier regroupant les entités lièe directement aux résidents : Chambre, Adherent et Ordinateur

# coding=utf8
from django.db import models
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

##Entité qui represente une chambre de la résidence. Permet la conversion chambre->(switch,port)
class Chambre(models.Model):
    ##Numéro de la chambre, sert de clé primaire
    numero = models.CharField(max_length=4, primary_key=True, verbose_name="Numéro de la chambre")
    ##Réfecence pour le switch associé
    switch = models.CharField(max_length=2, verbose_name="Switch relie à la chambre")
    ##Numéro du port associé a la chambre
    port = models.IntegerField(verbose_name="Numéro de port de la chambre")

    ##Affichage de la chambre
    def __str__(self):
        return "{0}".format(self.numero)

##Entité qui représente un adhérent de l'association, beneficiant des droits.
class Adherent(models.Model):
    ##Nom de famille de l'adhérent (transcripté automatiquement en majuscule)
    nom = models.CharField(max_length=45, verbose_name="Nom de famille")
    ##Prénom de l'adhérent (La prmière lettre est automatiquement mise en majuscule, les autres en minuscule
    prenom = models.CharField(max_length=30, verbose_name="Prénom")
    ##E-mail de l'adhérent, pour les mailing et l'envoi des mot de passe wifi
    mail = models.EmailField(max_length=150, verbose_name="e-mail de contact")
    #chambre = models.CharField(max_length=4, verbose_name="Numéro de chambre", validators=[
    #    RegexValidator(regex=r'^[A-DH][0-3]((0[0-9])|(1[0-3]))$', message="Erreur: cette chambre ne peut exister")],
    #                            unique=True, null=True)

    ##Chambre de l'adhérent, relation OneToOne vers une chambre
    chambre = models.OneToOneField(Chambre, verbose_name="Chambre de l'adhérent", related_name='locataire', null=True)
    ##Date à laquelle on va couper l'adhérent, sert dans le script prévu a cet effet
    dateExpiration = models.DateField(verbose_name="Date de coupure de l'adhérent",
                                      default=timezone.now().date())  # date limite avant la coupure de l'adherent
    ##Un commentaire sur l'adhérent
    commentaire = models.TextField(blank=True, verbose_name="Commentaire sur l'adhérent")
    ##Définit si l'adhérent est un rezoman, ce qui implique la désactivation du filtrage MAC sur sa chambre
    estRezoman = models.BooleanField(default=False,
                                     verbose_name="statut de Rezoman")
    ##Etat de l'adhérent, qui compare juste la date d'expiration a celle d'aujourd'hui, sert essentiellement à l'affichage"""
    estValide = models.BooleanField(default=False,
                                    verbose_name="l'adherent est valide")  # Si l'adhérent à accès aux services du rezo.
    ##Identifiant pour les accès Wifi
    identifiant = models.CharField(max_length=42, verbose_name="Identifiant du wifi", unique=True)
    ##Mot de passe autogénéré et haché par les fonctions id_generator et create_NT_hashed_password_v2 pour la connexion WiFi
    passwordWifi = models.BinaryField(max_length=1000, verbose_name="Mot de passe pour le Wifi (encrypt0é)", default=b'')

    ##Retourne une chaîne de caractère caractéristique de l'adhérent
    #@param self Réference de l'adhérent
    def __str__(self):
        return "{0} ".format(self.nom).upper() + "{0}".format(self.prenom).capitalize()

    ##Surcharge de la fonction d'enregistrement, qui s'occupe de formater les entrées préalablement
    #@param self Réference de l'adhérent
    #@param *argc liste d'arguments optionnels
    #@param **argv dictionnaire d'arguments optionnels
    def save(self, *argc, **argv):
        # On met a jour le statut et on formate les chaînes.
        self.estValide = (self.dateExpiration >= timezone.now().date())
        self.nom = self.nom.upper()
        self.prenom = self.prenom.capitalize()
        try:
            adhr = Adherent.objects.get(pk=self.pk)
        except Adherent.DoesNotExist:
            adhr=None
        # Controle de l'etat de la chambre pour la libérer si nécéssaire.
        if adhr is not None and self.chambre.locataire != adhr:
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

    ##Surcharge de la fonction originelle afin de ne pas controler ici l'unicité de la chambre
    #@param self Réference de l'adhérent
    #@param exclude paramètre de la fonction mère qui permet de prendre des champs a exclure de la verification
    def validate_unique(self, exclude=None):
        exclude.append('chambre')  # On ajoute la chambre au champs dont on ne verifie pas l'unicité.
        super(Adherent, self).validate_unique(exclude)

##Crée une chaine de caractère aléatoire de longueur fixé
#@param size taille de la chaine voulue
#@param chars liste des caractère admissible dans la chaine
def id_generator(size, chars=string.ascii_uppercase + string.digits+string.ascii_lowercase):
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))

##Encode le mot de passe au format md4, utilisé par le projet du serveur Wifi"""
#@param passwd Password à encoder
#@param user utilisateur liée a ce password
#@param domain non de dommaine utilise pour l'encodage
def create_NT_hashed_password_v2(passwd, user, domain):
    digests = hashlib.new('md4', passwd.encode('utf-16le')).digest()
    return hmac.new(digests, (user.upper()+domain).encode('utf-16le')).digest()

##Entité représentant les ordinateurs. Ils definissent l'IP et la MAC d'une carte pour un PC autorisé"""
class Ordinateur(models.Model):
    ##Non autogénéré comme entrée DNS pour cette carte, egalement clé primaire de l'entité Ordinateur
    nomDNS = models.CharField(max_length=20, primary_key=True, verbose_name="nom indice du PC")
    ##Vrai si le PC est enregistré dans la liste DNS
    DNSactif = models.BooleanField(verbose_name="non DNS actif ?", default=False)
    ##Adresse MAC de la carte concernée
    adresseMAC = models.CharField(max_length=17, validators=[
        RegexValidator(regex=r'^([a-fA-F0-9]{2}[: ;]?){5}[a-fA-F0-9]{2}$', message="Adresse MAC invalide")],
                                  verbose_name="Adresse MAC")
    ##IP attribué à cette carte
    adresseIP = models.GenericIPAddressField(protocol='IpV4', verbose_name="IP dynamique", unique=True)
    ##Relation OneToMany vers l'adhérent qui possède cette carte réseau
    proprietaire = models.ForeignKey(Adherent, verbose_name="Possesseur de l'ordinateur",
                                     related_name='listeOrdinateur')
    ##Défini si c'est une carte Wifi
    carteWifi = models.BooleanField(verbose_name="Carte Wifi ?", default=False)


    ##Préremplie la liste des IP disponible en fonction de celle en BDD
    #@param cls Réference de la classe Ordinateur
    #@param taille nombre d'IP que l'on se permet d'allouer
    @classmethod
    def genererListeInitiale(cls, taille=1024):
        pile = []
        for i in range(taille, -1, -1):
            ipChaine = "10.2."
            ipChaine += "{0}.{1}".format((i // 256) + 1, i % 256)
            try:
                Ordinateur.objects.get(adresseIP=ipChaine)
            except Ordinateur.DoesNotExist:
                pile.append(ipChaine)

        return pile

    ##Liste des IP disponible
    IP_pile = []  # Pile qui va contenir les IP disponible.

    ##Surcharge de la fonction de sauvegarde qui va s'occuper de formater les chaînes préalablement
    #@param self Réference de l'ordinateur
    #@param *argc liste d'arguments optionnels
    #@param **argv dictionnaire d'arguments optionnels
    def save(self, *argc, **argv):
        if len(self.__class__.IP_pile) == 0:  # Si la chaîne des adresse IP n'est pas crée
            self.__class__.IP_pile = self.__class__.genererListeInitiale()  # On la crée
        self.formatage()  # On formate les donnée et on enregistre en BDD
        super(Ordinateur, self).save(*argc, **argv)

    ##Renvoie une chaine de caractère decrivant l'entité concernée (le nom DNS)
    #@param self Reférence de l'ordinateur
    def __str__(self):
        return "PC {0}".format(self.nomDNS)

    ##Fonction qui s'occupe de mettre en forme les différentes chaînes de caractères avant l'enregistrement.
    #@param self Réference de l'ordinateur
    def formatage(self):
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

    ##Surcharge de la fonction delete qui reinsère l'IP dans la liste lors de la supréssion
    #@param self Réference de l'ordinateur
    #@param using paramètre de la fonction mère de django
    def delete(self, using=None):
        self.__class__.IP_pile.a
        super(Ordinateur, self.delete(using))
