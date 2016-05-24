#! /usr/bin/python
# -*- coding: UTF-8 -*-

import sys
#
#  Считываем url-list и шаблон конфига
file = open('/home/dieul/Документы/Selectel/download bad sites/dump.xml', 'r')
InUrls=file.read()
file.close()
# считываем делитель строки
divide=raw_input("Please enter the divide: ")
# init
end=InUrls.find(divide)
begin=InUrls.find("http")
beginr=InUrls.rfind("http",0,end)
print("begin",begin,"beginr",beginr,"end",end)
#открываем файл на запись URLs
file = open('/home/dieul/Документы/Selectel/download bad sites/MyUrls_after_my_parser', 'w')
while (end>=0)and(begin>=0):
    if begin<end:
        if begin == beginr:
            file.write(InUrls[begin:end]+'\n')
            print(InUrls[begin:end])
            InUrls=InUrls[end+1:len(InUrls)+1]
        else:
            file.write(InUrls[beginr:end]+'\n')
            print(InUrls[beginr:end])
            InUrls=InUrls[end+1:len(InUrls)+1]
    else:
        InUrls=InUrls[begin:len(InUrls)+1]

    end=InUrls.find(divide)
    begin=InUrls.find("http")
    beginr=InUrls.rfind("http",0,end)
    print("begin",begin,"beginr",beginr,"end",end)

file.close()
print("test")
print("test2")

