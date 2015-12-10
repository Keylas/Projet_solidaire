from django.db import models
from module_Adherent.models import Adherent

class Mailing(models.Model):
	nom = models.CharField(max_length=25, verbose_name="Nom de la mailing")
	gerant = models.ForeignKey(Adherent, verbose_name="Maitre de la mailing", related_name='mailingGerant')
	membres = models.ManyToManyField(Adherent, verbose_name="Membres", related_name='mailingMembre')

	def __str__(self):
		return "Mailing {0} géré par {1}".format(self.nom, self.gerant)

	def save(self, *argc, **argv):
		try:
			self.membres.get(pk=self.gerant.pk)
		except self.DoesNotExist:
			self.membre.add(self.gerant)

		super(self, Mailing).save(*argc, **argv)
