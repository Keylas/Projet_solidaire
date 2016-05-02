#fuck ....

import threading
import datetime
from siteWeb_solidaire.ressourcesAdherent.models import Adherent
from django.shortcuts import get_object_or_404

class Donnee():
    liste = []
    timer = None
    dateFin = None

def editionDate(adhrId):
    if Donnee.liste == None:
        initialiserListe()
    adhr = None
    try:
        adhr = Adherent.objects.get(pk=adhrId)
    except Adherent.DoesNotExist:
        return

    if adhr.dateExpiration == Donnee.dateFin:
        Donnee.liste.append(adhrId)
    elif adhr.dateExpiration < Donnee.dateFin:
        Donnee.dateFin = adhr.dateExpiration
        tps = calculerDuree(Donnee.dateFin)
        Donnee.liste = [adhrId]
        Donnee.timer = threading.Timer(tps, executerCoupure)


def calculerDuree(dateLimite):
    delta = dateLimite - datetime.datetime.now().date()
    return delta.seconds


def executerCoupure():
    if datetime.datetime.now().date() != Donnee.dateFin:
        initialiserListe()
        return
    adhrListe = Adherent.objects.filter(dateExpiration=Donnee.dateFin)
    for adhr in adhrListe:
        adhr.estValide = False
        adhr.save()

    initialiserListe()

def initialiserListe():
    Donnee.liste = []
    Donnee.dateFin = None
    list = Adherent.objects.all().order_by('dateExpiration')
    for adhr in list:
        if Donnee.dateFin == None:
            Donnee.dateFin = adhr.dateExpiration
        if adhr.dateExpiration > Donnee.dateFin:
            break
        Donnee.liste.append(adhr.pk)

    Donnee.timer = threading.Timer(calculerDuree(Donnee.dateFin), executerCoupure())