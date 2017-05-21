#!/usr/bin/python
import platform
import requests
import json

print ('python version '+platform.python_version())

URL='https://www.nespresso.com/cn/en/getQuickCapsules/original'
HEADER = {"Content-Type": "application/json; charset=UTF-8","Content-Length": "4"}

r = requests.post(url=URL, data='null', headers=HEADER)
print(r.status_code, r.reason)
json = json.loads(r.text)

for range in json['capsuleRange']:
    for list in range['capsuleList']:
        name = list['name'].encode('utf-8')
        price = list['priceValue']
        id = list['code'].encode('utf-8')
        type = list['type'].encode('utf-8')
        iconHref = list['mediaQuickOrder']['url'].encode('utf-8')
        print (id+" "+type+" "+name+" "+str(price) +" "+iconHref)
