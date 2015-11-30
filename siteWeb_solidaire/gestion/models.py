from django.db import models
from django_enumfield import enum
from django.contrib.auth.models import User

class RoleRezoman(enum.Enum):
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

	_transitions = {
		ENCAISSE: (RECEPTIONNE,),
		RECEPTIONNE: (DECLARE,)
	}
	
class Utilisateur(models.Model):
	user = models.OneToOneField(User, verbose_name="identifiants de connexion")
	role = enum.EnumField(RoleRezoman, default=RoleRezoman.MEMBRE, verbose_name="statut du rezoman")
	
	def __str__(self):
		return "{0}, {1}".format(self.user.username, RoleRezoman.reverse(self.role))
	
class Log(models.Model):
	date = models.DateTimeField(auto_now_add=True, auto_now=False)
	description = models.TextField(null=False)
	editeur = models.ForeignKey('utilisateur')
	
	def __str__(self):
		return "Log du {0} exécuté par {2} : {1}".format(self.date, self.description, self.editeur)

class Payement(models.Model):
	dateExecution = models.DateTimeField(auto_now_add=True, editable=False)
	montantFictif = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Montant à créditer")
	montantReel = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Montant réel payé")
	commentaire = models.TextField(null=True, verbose_name="Commentaire du créateur, à remplir si les deux montants sont différents")
	banque = models.CharField(null=True, max_length=42)
	etat = enum.EnumField(EtatPayement, default=EtatPayement.DECLARE)
#	beneficiaire = models.ForeignKey('donnees.adherent')
	
	def __str__(self):
		return "Payement de {0} euros à compter du {1}".format(self.montantFictif, self.dateExecution)

