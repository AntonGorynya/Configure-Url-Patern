#! /usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import argparse
import paramiko
import socket
from time import sleep

Hostname = "Host"
Flag = 0
#значение тэга
value = ""
#значение тэгов
valuem = ""
#количесво значений   в пременной value
step=1
#Количество <value> xxx </value> / step
stepv=15
i=0


# Считываем url-list и шаблон конфига
file = open('/home/dieul/Документы/Selectel/url-abuse_test.txt', 'r')
Urls=file.read()
file.close()
Urls=Urls.replace('\n', ' ').rstrip()
#print("Url_List is",Urls)
count=Urls.count(' ')
#отладка
print("Count space is ",count)
print("Length is", len(Urls))
# задаем управляющие команды

CLOSE = """
<rpc>
 	<close-session/>
</rpc>
]]>]]>"""

INFO="""
<rpc>
	<get-software-information/>
</rpc>
]]>]]>"""
CONF="""
<rpc>
        <get-configuration format="xml">
        </get-configuration>
</rpc>
]]>]]>"""
def mset(Hostname, Urls):
    SET="""
    <rpc>
    	<edit-config>
		<target>
			<candidate/>
		</target>
		<config>
			<configuration>
				<system>
					<host-name>"""+Hostname+"""</host-name>
				</system>
				<security>
					<utm>
						<custom-objects>
							<url-pattern>
								 <name>BadSites</name>
                                                                 <value>"""+Urls+"""</value>
							</url-pattern>
						</custom-objects>
					</utm>
				</security>
			</configuration>
		</config>
	</edit-config>
    </rpc>
    ]]>]]>
    """
    return SET

COMMIT="""
<rpc>
	<commit-configuration/>
</rpc>
"""

def createParser():
    parser = argparse.ArgumentParser(description = '--> Connect to vSRX <--')
    parser.add_argument("--host", default="10.230.242.11", action="store", help="hostname or IP ")
    parser.add_argument("-u", default="admin", action="store" , help = "username")
    parser.add_argument("-p", default="QaZxSw!23", action="store",help = "password")
    parser.add_argument("-P", default=830, action="store",help = "port")
    return parser

parser = createParser()
namespace = parser.parse_args(sys.argv[1:])

print (namespace)



#create socket
socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
socket.connect((namespace.host , namespace.P))

# шифруем через ssh
client = paramiko.SSHClient()
# добавляем ключ сервера в список известных хостов — файл .ssh/known_hosts.
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client = paramiko.Transport(socket)
client.connect( username=namespace.u, password=namespace.p)

#Create channel
channel = client.open_session()
name = channel.set_name('netconf')
#Invoke NETCON
channel.invoke_subsystem('netconf')

print("Last element",Urls[103:105])

#заполняем <value>
for i in range(1,count+1):
    position=Urls.rfind(' ')
    print(i,position,count)
    if (i)%step !=0:
        value=value+" "+Urls[position+1:len(Urls)+1]
        Urls=Urls[0:position]
    else:
#        создаем новую строчку  <value>
        valuem=valuem+value+"</value><value>"
#        print("Value in IF behin is %d %s" %(i, value))
        value=Urls[position+1:len(Urls)+1]
#        print("Value in IF end is",value)
#        print("Valuem in IF end is",valuem)
        Urls=Urls[0:position]
#отправка
    if i%stepv ==0:
        channel.send(mset(Hostname, valuem))
        sleep(0.1)
#        print(mset(Hostname, valuem))
        print("send  %d request successes!!!  count is %d " %(i, count))
        valuem = ""
#        print("Value in IF behin is %d %s" %(i, value))
    elif i == count:
        channel.send(mset(Hostname, valuem))
        channel.send(mset(Hostname, value))
        print("Value in IF behin is %d %s" %(i, value))
        print("Valuem in IF behin is %d %s" %(i, valuem))
        value=Urls[0:position-1]
        channel.send(mset(Hostname, value))
        print("First Value is :",value)
        sleep(0.1)
#        print(mset(Hostname, valuem))
        print("send  %d request successes!!!  count is %d " %(i, count))
        valuem = ""

#отправляем хвост
#channel.send(mset(Hostname, value))
#channel.send(mset(Hostname, valuem))
#print(Urls)
#position=Urls.rfind(' ')
#value=Urls[position+1:len(Urls)+1]
#print("value after if", value)
#valuem=valuem+value+"</value><value>"
#
#print("Tail send  %d request successes!!!  count is %d " %(i, count))

#channel.send(mset(Hostname, value))
#print("Value is",value)



#channel.send(INFO)
#channel.send(CONF)
#channel.send(SET)
channel.send(COMMIT)
Flag=1

#Recieve data returned
data = channel.recv(2048)
while data:
   data = channel.recv(1024)
   print(data)
   if (data.find('</rpc-reply>') == 0) and (Flag == 1):
     #We have reached the end of reply
     channel.send(CLOSE)

channel.close()
client.close()
socket.close()
