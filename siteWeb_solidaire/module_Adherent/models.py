from django.db import models
from django_enumfield import enum
from django.utils import timezone
from django.core.validators import RegexValidator

class Adherent(models.Model):
	nom = models.CharField(max_length=45, verbose_name="Nom de famille")
	prenom = models.CharField(max_length=30, verbose_name="Prénom")
	mail = models.EmailField(max_length=150, verbose_name="e-mail de contact")
	chambre = models.CharField(max_length=4, verbose_name="Numéros de chambre", validators=[RegexValidator(regex=r'^[A-DH][0-3][01][0-9]$', message="Erreur: cette chambre ne peut exister")], unique=True)
	dateExpiration = models.DateField(verbose_name="Date de coupure de l'adhérent", default=timezone.now)
	commentaire = models.TextField(blank=True, verbose_name="Commentaire sur l'adhérent")
	estRezoman = models.BooleanField(default=False, verbose_name="statut de Rezoman")
	estValide = models.BooleanField(default=False, verbose_name="l'adherent est valide")

	def __str__(self):
		return "{0}".format(nom).upper()+ "{0}".format(prenom).capitalize()


class Ordinateur(models.Model):
	nom = models.CharField(max_length=20, primary_key=True, verbose_name="nom indice du PC")
	adresseMAC = models.CharField(max_length=17, validators=[RegexValidator(regex=r'^([a-f0-9](2):)(5)[a-f0-9](2)$', message="Adresse MAC invalide")], verbose_name="Adresse MAC")
	adresseIP = models.GenericIPAddressField(protocol='IpV4', verbose_name="IP dynamique")
	possesseur = models.ForeignKey('Adherent', verbose_name="Possesseur de l'ordinateur")
	
	def __str__(self):
		return "PC {0}".format(nom)
# Create your models here
