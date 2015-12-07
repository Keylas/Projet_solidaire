from django.contrib import admin
from module_Adherent.models import Adherent, Ordinateur

class adminAdherent(admin.ModelAdmin):
	list_display = ('nom', 'prenom', 'dateExpiration', 'estValide')
	list_filter = ('estRezoman', 'estValide')
	date_hierarchy = 'dateExpiration'
	ordering = ('dateExpiration', )
	search_fields = ('nom', 'prenom', 'mail', 'chambre')
	description = "Adrérent du réseau"

class adminOrdinateur(admin.ModelAdmin):
	list_display = ('possesseur', 'adresseIP', 'adresseMAC')
	search_fields = ('possesseur', 'adresseIP', 'adresseMAC')
	description = "Ordinateur autorisé"


admin.site.register(Adherent, adminAdherent)
admin.site.register(Ordinateur, adminOrdinateur)

# Register your models here.
