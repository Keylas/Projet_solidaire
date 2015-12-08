#Fichier views de module_Adherent

from django.shortcuts import render
from django.http import HttpResponse
from module_Adherent.models import Adherent

def liste_adherent(request):
	
	temp = Adherent.objects.all() #On récupère tous les adhérents
	return render(request, 'adherents.html', {'all_adherent': temp}) #Les données sont passés dans la variable nommée all_adherent

def voir_adherent(request, id_adherent):
	text = "Ca, ce sera la fiche de l'adherent n°{0}".format(id_adherent)
	return HttpResponse(text)
