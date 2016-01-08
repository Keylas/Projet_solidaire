from django.db import models
from module_Adherent.models import Adherent

class Mailing(models.Model):
	adresse = models.CharField(max_length=25, verbose_name="Nom de la mailing")
	referant = models.ForeignKey(Adherent, verbose_name="Maitre de la mailing", related_name='listeMailingGere')
	listeAdherent = models.ManyToManyField(Adherent, verbose_name="Membres", related_name='listeMailing')

	
	def __str__(self):
		return "Mailing {0} géré par {1}".format(self.adresse, self.referant)

	def save(self, *argc, **argv):
		try:
			self.listeAdherent.get(pk=self.referant.pk)
		except self.DoesNotExist:
			self.listeAdherent.add(self.referant)

		super(self, Mailing).save(*argc, **argv)
