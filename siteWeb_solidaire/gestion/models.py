# coding=utf8

from django.db import models
from django_enumfield import enum
from django.contrib.auth.models import User
from ressourcesAdherent.models import Adherent
from django.core.exceptions import ValidationError

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

	#Défini les conditions de chamgement d'un etat à l'autre
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
	
class Log(models.Model):
	"""Entité des logs des activités des modérateurs"""
	date = models.DateTimeField(auto_now_add=True, auto_now=False)
	description = models.TextField(null=False)
	editeur = models.ForeignKey(Utilisateur, related_name='listeLog')
	
	def __str__(self):
		"""Renvoie une chaine de caractère représentative de l'entité"""
		return "Log du {0} exécuté par {2} : {1}".format(self.date, self.description, self.editeur)


class Payement(models.Model):
	"""Entité qui représente les payements"""
	beneficiaire = models.ForeignKey(Adherent, verbose_name="Membre créditeur", related_name='listePayement')
	rezoman = models.ForeignKey(Utilisateur, verbose_name="Rezoman créateur du payement", related_name='listePayement')
	dateCreation = models.DateTimeField(auto_now_add=True, editable=False)
	credit = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Montant à créditer")
	montantRecu = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Montant réel payé")
	commentaire = models.TextField(blank=True, verbose_name="Commentaire du créateur, à remplir si les deux montants sont différents")
	banque = models.CharField(blank=True, max_length=42)
	etat = enum.EnumField(EtatPayement, default=EtatPayement.DECLARE)
	
	
	def __str__(self):
		"""Renvoie une chaine de caractère représentative de l'entité"""
		return "Payement de {0} euros à compter du {1}".format(self.credit, self.dateCreation.date())

	def clean(self):
		super(Payement, self).clean()
		if self.montantRecu != self.credit and not self.commentaire:
			raise ValidationError({'commentaire': "Il faut justifier pourquoi les montants sont différents !"})

