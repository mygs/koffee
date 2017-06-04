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
    fxcache = {}
    forexList = getAllRecordsFromGoogleSheets('nespresso', 'forex')
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

def saveBlockConfig( writertypes, writerprices, date, country, localFX, json, fxcache ):
    for type in json['groups']:
        for coffees in type['products']:
            id = coffees['id'].encode('utf-8')
            name = coffees['name'].encode('utf-8')
            localPrice = coffees['price']
            iconHref = coffees['iconHref'].encode('utf-8')
            salesMultiple = coffees['addToCartButton']['salesMultiple']
            if salesMultiple == 10: #capsules!
                writertypes.writerow((country,id,name,iconHref))
                for forex in getAllRecordsFromGoogleSheets('nespresso', 'forex'):
                    #convertedPrice = currencyConvert (localPrice,fx,forex['code'])
                    convertedPrice = localPrice*fxcache[localFX, forex['code']]
                    writerprices.writerow((date,country,id,name,forex['code'],convertedPrice))
    return;

def saveQuickCapsules( writertypes, writerprices, date, country, localFX, json, fxcache ):
    for range in json['capsuleRange']:
        for list in range['capsuleList']:
            name = list['name'].encode('utf-8')
            localPrice = list['priceValue']
            id = list['code'].encode('utf-8')
            iconHref = list['mediaQuickOrder']['url'].encode('utf-8')
            salesMultiple = list['salesMultiple']
            if salesMultiple == 10:#capsules!
                writertypes.writerow((country,id,name,iconHref))
                for forex in getAllRecordsFromGoogleSheets('nespresso', 'forex'):
                    #convertedPrice = currencyConvert (localPrice,fx,forex['code'])
                    convertedPrice = localPrice*fxcache[localFX, forex['code']]
                    writerprices.writerow((date,country,id,name,forex['code'],convertedPrice))
    return;

##############################################
################### MAIN #####################
##############################################

startGlobal = time.time()
print ('python version '+platform.python_version())


start = time.time()
fxcache = getFXcache()
end = time.time()
minutes, seconds = divmod(end - start, 60)
print('FX Cache built in '+ str(minutes) + ' minutes and '+ str(int(seconds)) + ' seconds!')

timestamp = datetime.date.today().strftime("%Y%m%d")
os.chdir(sys.path[0]) # change working directory to script directory
csv_file_prices='./data/capsule-prices-'+timestamp+'.csv'
csv_file_types='./data/capsule-types-'+timestamp+'.csv'

fprices  = open(csv_file_prices, "wt")
ftypes  = open(csv_file_types, "wt")

try:
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
                start = time.time()
                saveBlockConfig(writertypes, writerprices, timestamp, country, fx, getNespressoBlockConfigJson(url), fxcache)
                end = time.time()
                print('Processed Nespresso(blockConfig) from '+ country+'. Took '+ str(int(end - start)) + ' seconds!')
            if locale['extract_strategy'] == 'quickCapsules':
                start = time.time()
                saveQuickCapsules(writertypes, writerprices, timestamp, country, fx, getNespressoQuickCapsulesJson(url), fxcache)
                end = time.time()
                print('\rProcessed Nespresso(quickCapsules) from '+ country+'. Took '+ str(int(end - start)) + ' seconds!')
finally:
    fprices.close()
    ftypes.close()

endGlobal = time.time()
globalMinutes, globalSeconds = divmod(endGlobal - startGlobal , 60)
print('\rAll process took '+ str(globalMinutes) + ' minutes and '+ str(int(globalSeconds)) + ' seconds!')
