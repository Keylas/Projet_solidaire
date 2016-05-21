# coding=utf8

from .Ecriture2 import SwitchA1, SwitchA2, SwitchB1, SwitchB2, SwitchC1, SwitchC2, SwitchD1, SwitchD2, SwitchH1, SwitchB3
from ressourcesAdherent.models import Adherent, Ordinateur, Chambres

def define_switch_port(chambre):
    """Fonction qui sert a faire le link entre la chambre et le couple switch/port"""
    fonction = None
    port = chambre.port
    if chambre.switch=="A1":
        fonction = SwitchA1.remplir
    elif chambre.switch=="A2":
        fonction = SwitchA2.remplir
    elif chambre.switch=="B1":
        fonction = SwitchB1.remplir
    elif chambre.switch=="B2":
        fonction = SwitchB2.remplir
    elif chambre.switch=="C1":
        fonction = SwitchC1.remplir
    elif chambre.switch=="C2":
        fonction = SwitchC2.remplir
    elif chambre.switch=="D1":
        fonction = SwitchD1.remplir
    elif chambre.switch=="D2":
        fonction = SwitchD2.remplir
    elif chambre.switch=="H1":
        fonction = SwitchH1.remplir
    else:
        fonction = SwitchB3.remplir
    return (fonction, port)

def script_InsertAdherent(adhrId):
    """Script qui est appelé sur le trigger de création de l'adhérent"""
    try:
        adhr = Adherent.objects.get(pk=adhrId)
        if adhr.chambre is None:
            return
    except Adherent.DoesNotExist:
        return
    (fncton, port) = define_switch_port(adhr.chambre)
    fncton("set interface ge-0/0/{0} unit 0 family ethernet-switching port-mode access".format(port))
    fncton("set interface ge-0/0/{0} unit 0 family ethernet-switching vlan members user".format(port))
    fncton("set ..... MAC-allowed {0}".format(adhr.listeOrdinateur.filter(carteWifi=False).count()))
    for ordi in adhr.listeOrdinateur:
        fncton("set ethernet-switching-option secure-access-port {0}".format(ordi.adresseMAC))

def script_DeleteAdherent(adhr):
    """Script qui est appelé sur le trigger de supression d'un adhérent"""
    if adhr.chambre is None:
        return
    (fncton, port) = define_switch_port(adhr.chambre)
    fncton("delete interface ge-0/0/{0} unit 0 family ethernet-switching".format(port))
    fncton("delete ethernet-switching-option secure-access-port interface ge-0/0/{0}".format(port)) #Histoire d'être sur !(fait par la supression des ordinateur normalement

def script_UpdateAdherent(adhrOld, adhr):
    """Script qui est appelé lors de l'édition d'un adhérent (déménagement, expiration, mail)"""
    if adhr.chambre != adhrOld.chambre:
        script_DeleteAdherent(adhr)
        script_InsertAdherent(adhr)
    if not adhr.estValide:
        if adhr.chambre is None:
            return
        (fncton, port) = define_switch_port(adhr.chambre)
        fncton("delete interface ge-0/0/{0} unit 0 family ethernet-switching".format(port))
    if adhr.mail != adhrOld.mail:
        print("changer pour mailing (si pas lecture reverse)")

def script_InsertOrdinateur(ordi):
    """Script qui est appelé lors de la création d'un ordinateur"""
    if ordi.carteWifi or ordi.proprietaire.chambre is None:
        return
    (fncton, port) = define_switch_port(ordi.proprietaire.chambre)
    fncton("set ethernet-switching-option secure-access-port interface ge-0/0/{0} mac-limit {1} action drop".format(port, ordi.proprietaire.listeOrdinateur.count()))
    fncton("set ethernet-switching-option secure-access-port interface ge-0/0/{0} allowed-mac {1}".format(port, ordi.adresseMAC))

def script_DeleteOrdinateur(ordi):
    """Script qui est appelé lors de la supression d'un ordinateur"""
    if ordi.carteWifi or ordi.proprietaire.chambre is None:
        return
    (fncton, port) = define_switch_port(ordi.proprietaire.chambre)
    fncton("delete ethernet-switching-option secure-access-port interface ge-0/0/{0} allowed-mac {1}".format(port, ordi.adresseMAC))
    fncton("set ethernet-switching-option secure-access-port interface ge-0/0/{0} mac-limit {1} action drop".format(port, ordi.proprietaire.listeOrdinateur.count()))

def script_updateOrdinateur(ordiOld, ordi):
    """Script qui est appelé lors de l'édition d'un ordinateur"""
    if ordi.carteWifi or ordi.proprietaire.chambre is None:
        return
    (fncton, port) = define_switch_port(ordi.proprietaire.chambre)
    fncton("delete ethernet-switching-option secure-access-port interface ge-0/0/{0} allowed-mac {1}".format(port, ordiOld.adresseMAC))
    fncton("set ethernet-switching-option secure-access-port interface ge-0/0/{0} allowed-mac {1}".format(port, ordi.adresseMAC))