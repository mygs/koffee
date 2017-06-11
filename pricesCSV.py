#!/usr/bin/python
import os
import sys
import platform
import urllib
import time
import datetime
import re
import csv
import json
import gspread
import requests
import pickle
from tqdm import tqdm
from oauth2client.service_account import ServiceAccountCredentials
from forex_python.converter import CurrencyRates

def getAllRecordsFromGoogleSheets(filename, sheetname):
    # use creds to create a client to interact with the Google Drive API
    SCOPE = ['https://spreadsheets.google.com/feeds']
    CREDS = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', SCOPE)
    client = gspread.authorize(CREDS)
    localesheet = client.open(filename).worksheet(sheetname)
    return localesheet.get_all_records()

def getFXcache():
    lastModification = 0
    if(os.path.isfile('fxcache.pkl')):
        lastModification = os.path.getmtime('fxcache.pkl')
    if (time.time() - lastModification <= 1800): # 30min
        with open('fxcache.pkl', 'rb') as f:
            return pickle.load(f)
    else:
        fxcache = {}
        forexList = getAllRecordsFromGoogleSheets('nespresso', 'forex')
        pbar = tqdm(total=len(forexList)**2,desc="Processing FX Cache")
        for forexFrom in forexList:
            for forexTo in forexList:
                fromCode = forexFrom['code']
                toCode = forexTo['code']
                rate = 0
                try:
                    rate = CurrencyRates().convert(toCode, fromCode, 1.0)
                except:
                    if fromCode == toCode:
                        rate = 1.0
                fxcache[toCode, fromCode] = rate
                pbar.update(1)
        with open('fxcache.pkl', 'wb') as f:
            pickle.dump(fxcache, f, pickle.HIGHEST_PROTOCOL)
        pbar.close()
        return fxcache

def getNespressoBlockConfigJson( _url ):
    PATTERN='var blockConfig =(.*),\n'
    if sys.version_info[0] == 2:
        class AppURLopener(urllib.FancyURLopener):version = "Mozilla/5.0"
    else:
        class AppURLopener(urllib.request.FancyURLopener):version = "Mozilla/5.0"
    req = AppURLopener().open(_url)
    webpage = req.read().decode('utf-8')
    blockConfigStr = re.search(PATTERN, webpage)
    blockConfig = json.loads(blockConfigStr.group(1))
    return blockConfig

def getNespressoQuickCapsulesJson( _url ):
    HEADER = {"Content-Type": "application/json; charset=UTF-8","Content-Length": "4"}
    r = requests.post(url=_url, data='null', headers=HEADER)
    quickCapsules = json.loads(r.text)
    return quickCapsules

def saveBlockConfig( writertypes, writerprices, date, country, localFX, json, fxcache, forexList ):
    pbar = tqdm(total=len(json['groups']),desc="Processing data from "+country)
    for type in json['groups']:
        for coffees in filter(lambda x: x['addToCartButton']['salesMultiple']== 10,type['products']):
            id = coffees['id'].encode('utf-8')
            name = coffees['name'].encode('utf-8')
            localPrice = coffees['price']
            iconHref = coffees['iconHref'].encode('utf-8')
            writertypes.writerow((country,id,name,iconHref))
            for forex in forexList:
                convertedPrice = localPrice*fxcache[localFX, forex['code']]
                writerprices.writerow((date,country,id,name,forex['code'],convertedPrice))
        pbar.update(1)
    pbar.close()
    return;

def saveQuickCapsules( writertypes, writerprices, date, country, localFX, json, fxcache, forexList ):
    pbar = tqdm(total=len(json['capsuleRange']),desc="Processing data from "+country)
    for capsulerange in json['capsuleRange']:
        for list in filter(lambda x: x['salesMultiple']== 10,capsulerange['capsuleList']):
            name = list['name'].encode('utf-8')
            localPrice = list['priceValue']
            id = list['code'].encode('utf-8')
            iconHref = list['mediaQuickOrder']['url'].encode('utf-8')
            writertypes.writerow((country,id,name,iconHref))
            for forex in forexList:
                convertedPrice = localPrice*fxcache[localFX, forex['code']]
                writerprices.writerow((date,country,id,name,forex['code'],convertedPrice))
        pbar.update(1)
    pbar.close()
    return;

##############################################
################### MAIN #####################
##############################################
startGlobal = time.time()
os.chdir(sys.path[0]) # change working directory to script directory
print ('python version '+platform.python_version())

fxcache = getFXcache()

timestamp = datetime.date.today().strftime("%Y%m%d")
csv_file_prices='./data/capsule-prices-'+timestamp+'.csv'
csv_file_types='./data/capsule-types-'+timestamp+'.csv'

fprices  = open(csv_file_prices, "wt")
ftypes  = open(csv_file_types, "wt")

try:
    forexList = getAllRecordsFromGoogleSheets('nespresso', 'forex')
    writerprices = csv.writer(fprices, delimiter=';')
    writertypes = csv.writer(ftypes, delimiter=';')

    writerprices.writerow( ('date','country','id','name','fx', 'price') )
    writertypes.writerow( ('country','id','name','iconHref') )
    for locale in getAllRecordsFromGoogleSheets('nespresso', 'locale'):
        if locale['status'] == 'ok':
            fx = locale['fx']
            country = locale['country']
            url = locale['capsules_url']
            if locale['extract_strategy'] == 'blockConfig':
                saveBlockConfig(writertypes, writerprices, timestamp, country,
                                fx, getNespressoBlockConfigJson(url), fxcache, forexList)
            if locale['extract_strategy'] == 'quickCapsules':
                saveQuickCapsules(writertypes, writerprices, timestamp, country,
                                fx, getNespressoQuickCapsulesJson(url), fxcache, forexList)
finally:
    fprices.close()
    ftypes.close()

endGlobal = time.time()
globalMinutes, globalSeconds = divmod(endGlobal - startGlobal , 60)
print('All process took '+ str(globalMinutes) + ' minutes and '+ str(int(globalSeconds)) + ' seconds!')
