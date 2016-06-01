#! /usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import argparse
import paramiko
import socket
from xml.dom.minidom import  parse,parseString
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
vendor=""

# Считываем url-list
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
#hello for cisco
HELLOC="""
<?xml version="1.0" encoding="UTF-8"?>
<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <capabilities>
        <capability>urn:ietf:params:netconf:base:1.0</capability><capability>urn:ietf:params:netconf:capability:writeable-running:1.0</capability>
        <capability>urn:ietf:params:netconf:capability:startup:1.0</capability><capability>urn:ietf:params:netconf:capability:url:1.0</capability>
        <capability>urn:cisco:params:netconf:capability:pi-data-model:1.0</capability><capability>urn:cisco:params:netconf:capability:notification:1.0</capability>
    </capabilities>
</hello>]]>]]>
"""
#hello for jun
HELLOJ = '<hello><capabilities><capability>urn:ietf:params:xml:ns:netconf:base:1.0</capability><capability>' \
        'urn:ietf:params:xml:ns:netconf:capability:candidate:1.0</capability><capability>urn:ietf:params:xml:ns:' \
        'netconf:capability:confirmed-commit:1.0</capability><capability>urn:ietf:params:xml:ns:netconf:capability:' \
        'validate:1.0</capability><capability>urn:ietf:params:xml:ns:netconf:capability:url:1.0?protocol=http,ftp,file' \
        '</capability><capability>http://xml.juniper.net/netconf/junos/1.0</capability><capability>http://xml.juniper.' \
        'net/dmi/system/1.0</capability></capabilities></hello>' \
        ']]>]]>'
#как для cisco так и для jun
CLOSE = """
<rpc>
 	<close-session/>
</rpc>
]]>]]>"""
#JUN
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
#CISCO
CONFC="""
<?xml version="1.0" encoding=\"UTF-8\"?>
<rpc message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <get>
        <filter>
            <config-format-text-cmd>
                <text-filter-spec> | include interface </text-filter-spec>
            </config-format-text-cmd>
            <oper-data-format-text-block>
                <exec>show interfaces</exec>
                <exec>show arp</exec>
            </oper-data-format-text-block>
        </filter>
    </get>
</rpc>]]>]]>
"""
CONFC2="""
 <?xml version="1.0" encoding="UTF-8"?>
<rpc>
    <get-config>
        <source>
            <startup/>
        </source>
        <filter>
            <config-format-xml>
            </config-format-xml>
        </filter>
    </get-config>
</rpc>]]>]]>
"""
def msetc(Hostname,pattern):
    SETC="""
    <?xml version="1.0" encoding="UTF-8"?>
    <rpc message-id="netconf.mini.edit.3">
        <edit-config>
            <target>
                <startup/>
          </target>
        <config>
        <cli-config-data-block>
        hostname """+Hostname+"""
        parameter-map type regex BadSitesRegex \n"""+pattern+""" </cli-config-data-block>
        </config>
        </edit-config>
    </rpc>]]>]]>  """
    return SETC

def msetj(Hostname, Urls):
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
    parser = argparse.ArgumentParser(description = '--> Connect to vSRX or 2851 <--')
    parser.add_argument("--host", default="10.230.128.166", action="store", help="hostname or IP ")
    parser.add_argument("-u", default="admin", action="store" , help = "username")
    parser.add_argument("-p", default="QaZxSw!23", action="store",help = "password")
    parser.add_argument("-P", default=830, action="store",help = "port")
    parser.add_argument("-d", action="store_true", help = "debug")
    parser.add_argument("-v", action="store_true", help = "verbose")
    return parser

parser = createParser()
namespace = parser.parse_args(sys.argv[1:])

print (namespace)


if namespace.d == False:
    #create socket
    socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    socket.connect((namespace.host , int(namespace.P)))
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
    #Прием начальной информации.
    data =1
    data_hello=""
    #для теста
    i = 0
    while data:
        #для дебага
        print("номер итерации %i \n Значение пременной data_hello " %i)
        i=i+1
        data = channel.recv(4096)
        data_hello=data_hello+data
        #для дебага
        print(data_hello)
        #ищем конец Hello сообщения и определяем вендора
        if data_hello.find('</hello>') != -1:
            if (data_hello.find("cisco") != -1):
                vendor="cisco"
                mset=msetc
                channel.send(HELLOC)
                #сделаем запрос на кофиг
                #channel.send(CONFC)
                #стереть потом
                data_hello=""
            elif (data_hello.find("juniper") != -1):
                vendor="juniper"
                mset=msetj
                channel.send(HELLOJ)
            else:
                print("not supported")
            if namespace.v == True:
                print(data_hello)
                print("End of Hello message is found")
                print("gnerate hello message...and send it")
                if vendor == "juniper":
                    print(HELLOJ)
                elif vendor == "cisco":
                    print(HELLOC)
            break
else:
    mset=msetc
    vendor="cisco"
#выдергиваем тэг <session-id>
#    dom=parseString(data_hello)
    #выдерает вместе с тэгом
#    session_id=dom.getElementsByTagName('session-id')[0].toxml()
    # выдерает только значение, можно было бы сделать цикл for node in
    # session-id: print node.childNodes[0].nodeValue
#    session_id=dom.getElementsByTagName('session-id')[0].childNodes[0].nodeValue

#       ENABLE="""
#        <rpc><notification-on/>
#        </rpc>
#        """
#        channel.send(ENABLE)
#    while 1:
#        print("in while")
#        data = channel.recv(4096)
#        print(data)
#        if data.find('</rpc-reply>') != -1:
#            decision=raw_input("are u vendnor %s? is it right? Ready to go?" %vendor)
#            channel.send(CLOSE)
#            break

decision=raw_input("!!!!are u vendnor %s? is it right? Ready to go?" %vendor)




#заполняем <value>
for i in range(1,count+1):
    position=Urls.rfind(' ')
    print(i,position,count)
    if (i)%step !=0:
        value=value+" "+Urls[position+1:len(Urls)+1]
        Urls=Urls[0:position]
    else:
        if vendor == "juniper":
#        создаем новую строчку  <value>
            valuem=valuem+value+"</value><value>"
        else:
            value="pattern "+value+" \n"
            valuem=valuem+value
#        print("Value in IF behin is %d %s" %(i, value))
        value=Urls[position+1:len(Urls)+1]
#        print("Value in IF end is",value)
#        print("Valuem in IF end is",valuem)
        Urls=Urls[0:position]
#отправка
    if i%stepv ==0:
        if namespace.d == False:
            channel.send(mset(Hostname, valuem))
            if namespace.v == True:
                print(mset(Hostname, valuem))
        else:
            print(mset(Hostname, valuem))
        sleep(0.1)
        print("send  %d request successes!!!  count is %d " %(i, count))
        valuem = ""
    elif i == count:
        if vendor=="cisco":
            value="pattern "+value
        if namespace.d == False:
            channel.send(mset(Hostname, valuem))
            channel.send(mset(Hostname, value))
            if namespace.v == True:
                print(mset(Hostname, valuem))
                print(mset(Hostname, value))
        else:
            print(mset(Hostname, valuem))
            print(mset(Hostname, value))
        print("Value in IF behin is %d %s" %(i, value))
        print("Valuem in IF behin is %d %s" %(i, valuem))
        if vendor == "juniper":
            value=Urls[0:position-1]
        else:
            value="patern "+Urls[0:position-1]
        if namespace.d == False:
            channel.send(mset(Hostname, value))
            if namespace.v == True:
                print(mset(Hostname, value))
        else:
            print(mset(Hostname, value))
        sleep(0.1)
        print("send  %d request successes!!!  count is %d " %(i, count))
        valuem = ""

#channel.send(INFO)
#channel.send(CONF)
#channel.send(SET)

if namespace.d == False:
    channel.send(COMMIT)
    if namespace.v == True:
        print(COMMIT)
    Flag=1
    #Recieve data returned
    data = channel.recv(2048)
    while data:
       data = channel.recv(1024)
       print(data)
       if (data.find('</rpc-reply>') != -1) and (Flag == 1):
         #We have reached the end of reply
         channel.send(CLOSE)

    channel.close()
    client.close()
    socket.close()
else:
    print(COMMIT)
