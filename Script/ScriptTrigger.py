from .Ecriture2 import SwitchA1, SwitchA2, SwitchB1, SwitchB2, SwitchC1, SwitchC2, SwitchD1, SwitchD2, SwitchH1

def define_switch_port(chambre):
    fonction = None
    port = None
    if chambre[0]=='B':
        if int(chambre[1]) < 2:
            fonction = SwitchB1.remplir
            port = int(chambre[2:])+(int(chambre[1])*13)-1
        else:
            fonction = SwitchB2.remplir
            port = int(chambre[2:])+13*(int(chambre[1])-2)-1
    return (fonction, port)

#Adherent_insert
def script_InsertAdherent(adhr):
    (fncton, port) = define_switch_port(adhr.chambre)
    fncton("set interface ge-0/0/{0} unit 0 family ethernet-switching port-mode access".format(port))
    fncton("set interface ge-0/0/{0} unit 0 family ethernet-switching vlan members user".format(port))
