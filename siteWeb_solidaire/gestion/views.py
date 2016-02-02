from django.shortcuts import render
from django.views.generic import ListView
from .models import Log

# Create your views here.

def test(request):
	return render(request, "layoutBase.html")

class ListeLog(ListView):
	model = Log
	context_object_name = "listeLog"
	template_name= "accueil.html"

	

