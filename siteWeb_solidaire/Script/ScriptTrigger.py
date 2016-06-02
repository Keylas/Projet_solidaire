# coding=utf8

import psycopg2, sys

sys.path.append("/home/corentin/ProjetWeb/projet_solidaire/siteWeb_solidaire/")
from Script.Ecriture2 import SwitchA1, SwitchA2, SwitchB1, SwitchB2, SwitchC1, SwitchC2, SwitchD1, SwitchD2, SwitchH1, SwitchB3

def define_switch_port(chambre):
    """Fonction qui sert a faire le link entre la chambre et le couple switch/port"""
    fonction = None
    port = chambre[1]
    if chambre[0]=="A1":
        fonction = SwitchA1.remplir
    elif chambre[0]=="A2":
        fonction = SwitchA2.remplir
    elif chambre[0]=="B1":
        fonction = SwitchB1.remplir
    elif chambre[0]=="B2":
        fonction = SwitchB2.remplir
    elif chambre[0]=="C1":
        fonction = SwitchC1.remplir
    elif chambre[0]=="C2":
        fonction = SwitchC2.remplir
    elif chambre[0]=="D1":
        fonction = SwitchD1.remplir
    elif chambre[0]=="D2":
        fonction = SwitchD2.remplir
    elif chambre[0]=="H1":
        fonction = SwitchH1.remplir
    elif chambre[0]=='B3':
        fonction = SwitchB3.remplir
    else:
        fonction = "ERREUR"
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

def script_InsertOrdinateur(ordi, cursor):
    """Script qui est appelé lors de la création d'un ordinateur"""
    if ordi['carteWifi']:
        return
    cursor.execute("SELECT switch, port FROM \"ressourcesAdherent_chambre\" WHERE numero = (SELECT chambre_id FROM \"ressourcesAdherent_adherent\" WHERE id={0});".format(ordi['proprietaire_id']))
    res = cursor.fetchone()
    (fncton, port) = define_switch_port(res)
    if fncton == "ERREUR":
        return
    cursor.execute("SELECT COUNT(*) FROM \"ressourcesAdherent_ordinateur\" WHERE proprietaire_id = {0};".format(ordi['proprietaire_id']))
    fncton("set ethernet-switching-option secure-access-port interface ge-0/0/{0} mac-limit {1} action drop".format(port, cursor.fetchone()[0]+1))
    fncton("set ethernet-switching-option secure-access-port interface ge-0/0/{0} allowed-mac {1}".format(port, ordi['adresseMAC']))

def script_DeleteOrdinateur(ordi, cursor):
    """Script qui est appelé lors de la supression d'un ordinateur"""
    if ordi['carteWifi']:
        return
    cursor.execute("SELECT switch, port FROM \"ressourcesAdherent_chambre\" WHERE numero = (SELECT chambre_id FROM \"ressourcesAdherent_adherent\" WHERE id={0});".format(ordi['proprietaire_id']))
    res = cursor.fetchone()
    (fncton, port) = define_switch_port(res)
    if fncton == "ERREUR":
        return
    cursor.execute("SELECT COUNT(*) FROM \"ressourcesAdherent_ordinateur\" WHERE proprietaire_id = {0};".format(ordi['proprietaire_id']))
    fncton("delete ethernet-switching-option secure-access-port interface ge-0/0/{0} allowed-mac {1}".format(port, ordi['adresseMAC']))
    fncton("set ethernet-switching-option secure-access-port interface ge-0/0/{0} mac-limit {1} action drop".format(port, cursor.fetchone()[0]-1))

def script_updateOrdinateur(dict, cursor):
    """Script qui est appelé lors de l'édition d'un ordinateur"""
    if dict['new']['carteWifi']:
        return
    cursor.execute("SELECT switch, port FROM \"ressourcesAdherent_chambre\" WHERE numero = (SELECT chambre_id FROM \"ressourcesAdherent_adherent\" WHERE id={0});".format(dict['new']['proprietaire_id']))
    res = cursor.fetchone()
    (fncton, port) = define_switch_port(res)
    if fncton == "ERREUR":
        return

    fncton("delete ethernet-switching-option secure-access-port interface ge-0/0/{0} allowed-mac {1}".format(port, dict['old']['adresseMAC']))
    fncton("set ethernet-switching-option secure-access-port interface ge-0/0/{0} allowed-mac {1}".format(port, dict['new']['adresseMAC']))

def traitementEvent(dict):
    try:
        conn = psycopg2.connect(database="db_superuser", user="superuser", password="superuser", host="localhost")
        cur = conn.cursor()
    except:
        print("ERREUR : Connexion impossible")
        return
    if dict['table_name'] == "ressourcesAdherent_ordinateur":
        if dict['event'] == "INSERT":
            script_InsertOrdinateur(dict['new'], cur)
        elif dict['event'] == "UPDATE":
            script_updateOrdinateur(dict, cur)
        elif dict['event'] == "DELETE":
            script_DeleteOrdinateur(dict['old'], cur)
        else:
            cur.close()
            conn.close()
            return
        SwitchB3.ecrire()
    elif dict['table'] == "Adherent":
        cur.close()
        conn.close()
        return
    else:
        cur.close()
        conn.close()
        return

def testEvent():
    dico = {'table':"Ordinateur", 'trigger':"INSERT", 'new':{'proprietaire':5, 'adresseMAC': "12:17:94:a1:e7:58", 'carteWifi':False}}
    traitementEvent(dico)

    dico['trigger']="UPDATE"
    dico['old'] = {'proprietaire':5, 'adresseMAC': "12:17:94:a1:e7:58", 'carteWifi':False}
    dico['new'] = {'proprietaire':5, 'adresseMAC': "18:a7:94:a1:e7:58", 'carteWifi':False}
    traitementEvent(dico)

if __name__ == '__main__':
    testEvent()