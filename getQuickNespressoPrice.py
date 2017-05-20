#!/usr/bin/python
import platform
import requests
import json

print ('python version '+platform.python_version())

URL='https://www.nespresso.com/cn/en/getQuickCapsules/original'
headersx = {
            #"Host": "www.nespresso.com",
            #"User-Agent": "Mozilla/5.0",
            #"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            #"Accept-Language": "en-US,en;q=0.5",
            #"Accept-Encoding": "gzip, deflate",
            "Content-Type": "application/json; charset=UTF-8",
            #"Referer": "https://www.nespresso.com/cn/en/Order-Capsules",
            "Content-Length": "4",
            #"Cookie": "STICKED-TO=R2073132993; _sdsat_AppVersion=NC2-classic; _sdsat_AppPlatform=desktop-site; nestmsStr=1495305908068; s_cc=true; s_fid=7F34E624C3ED1CC7-2B313CD7ECD6347D; c_m=undefinedDirect%20LoadDirect%20Load; s_channeltrafic_p=Direct%20Load; s_evar21=Direct%20Load_B2B; s_nr=1495306193160-New; s_vnum=1497897908406%26vn%3D1; s_sq=%5B%5BB%5D%5D; s_vi=[CS]v1|2C90475A851D3172-4000012B200084E7[CE]; JSESSIONID=94DFF4A537C0393612E52D27F4FD73FD; CKI_MARKET=cn; CKI_MARKET=cn; CKI_LANGUAGE=en; CKI_LANGUAGE=en; _sdsat_AppRelease=16.14.11; _ga=GA1.2.1579673648.1495306193; _gid=GA1.2.1991647544.1495306193",
            #"Connection": "keep-alive",
            #"Pragma": "no-cache",
            #"Cache-Control": "no-cache"
            }

r = requests.post(url=URL, data='null', headers=headersx)
print(r.status_code, r.reason)
json = json.loads(r.text)

for range in json['capsuleRange']:
    for list in range['capsuleList']:
        name = list['name']
        price = list['priceValue']
        id = list['code']
        type = list['type']
        iconHref = list['mediaQuickOrder']['url']
        print (id+" "+type+" "+name+" "+str(price) +" "+iconHref)
