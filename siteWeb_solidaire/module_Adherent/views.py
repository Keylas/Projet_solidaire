from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def liste_adherent(request):

 text = "Ici on fera en sorte de voir tous les adhérents"

 return HttpResponse(text)

def voir_adherent(request, id_adherent):

 text = "La fiche personnelle de l'adherent dont l'id est {0}".format(id_adherent)

 return HttpResponse(text)


