from .Ecriture2 import SwitchA1, SwitchA2, SwitchB1, SwitchB2, SwitchC1, SwitchC2, SwitchD1, SwitchD2, SwitchH1, SwitchB3
from ressourcesAdherent.models import Adherent, Ordinateur, Chambres

def define_switch_port(chambre):
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

#Adherent_insert
def script_InsertAdherent(adhr):
    if adhr.chambre is None:
        return
    (fncton, port) = define_switch_port(adhr.chambre)
    fncton("set interface ge-0/0/{0} unit 0 family ethernet-switching port-mode access".format(port))
    fncton("set interface ge-0/0/{0} unit 0 family ethernet-switching vlan members user".format(port))
    fncton("set ..... MAC-allowed {0}".format(adhr.listeOrdinateur.filter(carteWifi=False).count()))
    for ordi in adhr.listeOrdinateur:
        fncton("set ethernet-switching-option secure-access-port {0}".format(ordi.adresseMAC))

def script_DeleteAdherent(adhr):
    if adhr.chambre is None:
        return
    (fncton, port) = define_switch_port(adhr.chambre)
    fncton("delete interface ge-0/0/{0} unit 0 family ethernet-switching".format(port))
    fncton("delete ....")

def script_UpdateAdherent(adhrOld, adhr):
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
    if ordi.carteWifi or ordi.proprietaire.chambre is None:
        return
    (fncton, port) = define_switch_port(ordi.proprietaire.chambre)
    fncton("set ..... MAC-allowed {0}".format(ordi.proprietaire.listeOrdinateur.count()))
    fncton("set ethernet-switching-option secure-access-port {0}".format(ordi.adresseMAC))

def script_DeleteOrdinateur(ordi):
    if ordi.carteWifi or ordi.proprietaire.chambre is None:
        return
    (fncton, port) = define_switch_port(ordi.proprietaire.chambre)
    fncton("delete ethernet-switching-option secure-access-port {0}".format(ordi.adresseMAC))
    fncton("set ..... MAC-allowed {0}".format(ordi.proprietaire.listeOrdinateur.count()))

def script_updateOrdinateur(ordiOld, ordi):
    if ordi.carteWifi or ordi.proprietaire.chambre is None:
        return
    (fncton, port) = define_switch_port(ordi.proprietaire.chambre)
    fncton("delete ethernet-switching-option secure-access-port {0}".format(ordiOld.adresseMAC))
    fncton("set ethernet-switching-option secure-access-port {0}".format(ordi.adresseMAC))