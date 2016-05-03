from django.utils import timezone
from datetime import datetime, timedelta
from threading import Timer, Lock
from .models import Adherent

class Donnee():
    dateActuelle = timezone.now().date()
    listeId = []
    timer = None
    mutex = Lock()

def editionAdherent(id):
    adhr = None
    try:
        adhr = Adherent.objects.get(pk=id)
    except Adherent.DoesNotExist:
        return

    Donnee.mutex.acquire()
    if Donnee.timer is None:
        initialiserListe()
    if adhr.dateExpiration < Donnee.dateActuelle:
        Donnee.dateActuelle = adhr.dateExpiration
        Donnee.listeId = [id]
        Donnee.timer = Timer(calculTpsAttente(Donnee.dateActuelle), executerCoupure)
    elif adhr.dateExpiration == Donnee.dateActuelle:
        Donnee.listeId.append(id)
    Donnee.mutex.release()

def calculTpsAttente(dateFin):
    delta = datetime(day=dateFin.day, month=dateFin.month, year=dateFin.year) - datetime.now()
    return int(delta.total_seconds())

def initialiserListe():
    q1 = Adherent.objects.all().order_by('dateExpiration')
    Donnee.listeId = []
    date = q1[0].dateExpiration
    for adhr in q1:
        if adhr.dateExpiration > date:
            break
        Donnee.listeId.append(adhr.pk)
    Donnee.dateActuelle = date
    Donnee.timer = Timer(calculTpsAttente(date), executerCoupure)


def executerCoupure():
    Donnee.mutex.Lock()
    for id in Donnee.listeId:
        try:
            adhr = Adherent.objects.get(pk=id)
            adhr.estValide = False
            adhr.save()
            print("L'adherent {0} à été coupé".format(id))
        except Adherent.DoesNotExist:
            pass
    initialiserListe()
    Donnee.mutex.release()
