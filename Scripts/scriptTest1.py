from pexpect import pxssh
import sys



session=pxssh.pxssh() #creation de la session

if(session.login('192.168.255.24','superuser','Superuser',auto_prompt_reset=False)):
	print('success')	
	session.sendline('configure')
	session.sendline('set interfaces ge-0/0/'+str(sys.argv[1])+' unit 0 family ethernet-switching port-mode '+str(sys.argv[2]))	
	session.sendline('commit')
	session.sendline('exit')
	session.sendline('exit')
	session.logout()
	print('logout')

print('fin')



