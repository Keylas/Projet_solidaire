from django.db import models
from django_enumfield import enum
from django.utils import timezone
from django.core.validators import RegexValidator, MinValueValidator

class Adherent(models.Model):
	"""Models des adhérents qui permet la gestion administrative"""
	nom = models.CharField(max_length=45, verbose_name="Nom de famille")
	prenom = models.CharField(max_length=30, verbose_name="Prénom")
	mail = models.EmailField(max_length=150, verbose_name="e-mail de contact")
	chambre = models.CharField(max_length=4, verbose_name="Numéro de chambre", validators=[RegexValidator(regex=r'^([A-DH][0-3][01][0-9])?$', message="Erreur: cette chambre ne peut exister")], unique=True, null=True) #^[([A-D][0-3])(H[0-2])][(0[1-9])(1[0-3])]$
	dateExpiration = models.DateField(verbose_name="Date de coupure de l'adhérent", default=timezone.now)
	commentaire = models.TextField(blank=True, verbose_name="Commentaire sur l'adhérent")
	estRezoman = models.BooleanField(default=False, verbose_name="statut de Rezoman")
	estValide = models.BooleanField(default=False, verbose_name="l'adherent est valide")

	def __str__(self):
		return "{0} ".format(self.nom).upper()+ "{0}".format(self.prenom).capitalize()

	def save(self, *argc, **argv):
		"""Surcharge de la fonction d'enregistrement, qui s'occupe de formater les entrées préalablement"""
		self.estValide = (self.dateExpiration >= timezone.now().date())
		self.nom = self.nom.upper()
		self.prenom = self.prenom.capitalize()

		#Partie non fonctionnelle, on ne peut chasser une personne de sa chambre manuellement.
		if self.chambre: #Si la chambre n'est pas vide (renseigner)
			try: #On verifie si la chambre est déjà assigné pour la vider dans ce cas
				adhr = Adherent.objects.get(chambre=self.chambre)
				adhr.chambre = None
				adhr.save()
			except Adherent.DoesNotExist: #Cas ou la chambre est libre
				pass
		try:
			super(Adherent, self).validate_unique()
			super(Adherent, self).save(*argc, **argv)
		except ValidationError:
			pass

	def validate_unique(self, exclude=None):
		exclude.append('chambre')
		super(Adherent, self).validate_unique(exclude)

class Ordinateur(models.Model):
	"""Model des objets représentant les ordinateurs. Ils definissent l'IP et la MAC du PC autorisé"""

	nom = models.CharField(max_length=20, primary_key=True, verbose_name="nom indice du PC")
	adresseMAC = models.CharField(max_length=17, validators=[RegexValidator(regex=r'^([a-fA-F0-9]{2}[: ;]?){5}[a-fA-F0-9]{2}$', message="Adresse MAC invalide")], verbose_name="Adresse MAC")
	adresseIP = models.GenericIPAddressField(protocol='IpV4', verbose_name="IP dynamique", unique=True)
	possesseur = models.ForeignKey('Adherent', verbose_name="Possesseur de l'ordinateur")
	IP_compteur = 0;	

	def save(self, *argc, **argv):
		"""Surcharge de la fonction de sauvegarde qui va s'occuper de formater les chaînes préalablement"""
		self.formatage()
		super(Ordinateur, self).save(*argc, **argv)
	def __str__(self):
		return "PC {0}".format(self.nom)

	def formatage(self):
		"""Fonction qui s'occupe de mettre en forme les différentes chaînes de caractères avant l'enregistrement."""
		if self.nom=="":
			if len(self.possesseur.prenom) > 3:
		    		pren = self.possesseur.prenom[0:3]
			else:
				pren=self.possesseur.prenom
			chaine=self.possesseur.nom.lower().lstrip()+pren.lower()
			res = Ordinateur.objects.filter(nom__contains = chaine)
			self.nom = chaine + "{0}".format(res.count()+1)

		chtemp = self.adresseMAC.replace(' ', '')
		chtemp = chtemp.replace(':', '')
		chtemp = chtemp.replace(';', '')
		li = [chtemp[0:2],chtemp[2:4],chtemp[4:6],chtemp[6:8],chtemp[8:10],chtemp[10:12]]
		self.adresseMAC = ":".join(li)
