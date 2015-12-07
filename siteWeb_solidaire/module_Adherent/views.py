#Fichier views de module_Adherent

from django.shortcuts import render
from django.http import HttpResponse

def liste_adherent(request):
	text = "Ici on pourra voir la liste des adhérents"
	
	return HttpResponse(text)

def voir_adherent(request, id_adherent):
	text = "Ca, ce sera la fiche de l'adherent n°{0}".format(id_adherent)
	return HttpResponse(text)
