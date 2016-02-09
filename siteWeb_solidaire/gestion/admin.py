# coding=utf8

from django.contrib import admin
from gestion.models import Log, Utilisateur, Payement
# Register your models here.

class adminLog(admin.ModelAdmin):
	list_display = ('date', 'editeur', 'apercu_description')
	list_filter = ('date', 'editeur')
	date_hierarchy = 'date'
	ordering = ('date', )
	search_fields = ('description',)

	fields = ('editeur', 'description')
	def apercu_description(self, log):
		text = log.description[0:40]
		if len(log.description) > 40:
		    return '%s…' % text
		else:
		    return text
	apercu_description.short_description="Description du log"

class adminPayement(admin.ModelAdmin):
	list_display = ('beneficiaire', 'credit', 'montantRecu', 'etat')
	list_filter = ('dateCreation', 'etat')
	date_hierarchy = 'dateCreation'
	ordering = ('dateCreation', )
	search_fields = ('credit','montantRecu')
	exclude = ('etat',)

admin.site.register(Log, adminLog)
admin.site.register(Utilisateur)
admin.site.register(Payement, adminPayement)

