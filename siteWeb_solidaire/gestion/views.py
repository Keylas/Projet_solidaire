from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Log

# Create your views here.

def test(request):
	return render(request, "layoutBase.html")

#@method_decorator(login_required, name='dispatch')
class ListeLog(ListView):
	model = Log
	context_object_name = "liste_Log"
	template_name= "accueil.html"

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(ListeLog, self).dispatch(*args, **kwargs)

