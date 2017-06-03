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

def getNespressoBlockConfigJson( _url ):
    PATTERN='var blockConfig =(.*),\n'
    class AppURLopener(urllib.FancyURLopener):version = "Mozilla/5.0"
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

def currencyConvert (externalPrice, fx):
    try:
        preco = CurrencyRates().convert(fx, 'BRL', externalPrice)
    except:
        if fx == 'BRL':
            preco = externalPrice
        else:
            preco = None
    return preco

def saveBlockConfig( writer, date, country, fx, json ):
    for type in json['groups']:
        for coffees in type['products']:
            id = coffees['id'].encode('utf-8')
            name = coffees['name'].encode('utf-8')
            price = coffees['price']
            iconHref = coffees['iconHref'].encode('utf-8')
            salesMultiple = coffees['addToCartButton']['salesMultiple']
            preco = currencyConvert(price, fx)
            if salesMultiple == 10 and preco != None:
                writer.writerow( (date,country,id,name,price,preco,iconHref))
    return;

def saveQuickCapsules( writer, date, country, fx, json ):
    for range in json['capsuleRange']:
        for list in range['capsuleList']:
            name = list['name'].encode('utf-8')
            price = list['priceValue']
            id = list['code'].encode('utf-8')
            type = list['type'].encode('utf-8')
            iconHref = list['mediaQuickOrder']['url'].encode('utf-8')
            salesMultiple = list['salesMultiple']
            preco = currencyConvert(price, fx)
            if salesMultiple == 10 and preco != None:
                writer.writerow( (date,country,id,name,price,preco,iconHref))
    return;

##############################################
################### MAIN #####################
##############################################

startGlobal = time.time()
print ('python version '+platform.python_version())

timestamp = datetime.date.today().strftime("%Y%m%d")
os.chdir(sys.path[0]) # change working directory to script directory
csv_file='./data/capsule-prices-'+timestamp+'.csv'

f  = open(csv_file, "wt")
try:
    writer = csv.writer(f, delimiter=';')
    writer.writerow( ('date','country','id','name','localprice','brl','iconHref') )
    for locale in getAllRecordsFromGoogleSheets('nespresso', 'locale'):
        if locale['status'] == 'to_test':
            fx = locale['fx']
            country = locale['country']
            url = locale['capsules_url']
            if locale['extract_strategy'] == 'blockConfig':
                start = time.time()
                print('Processing blockConfig from '+ country),
                saveBlockConfig(writer, timestamp, country, fx, getNespressoBlockConfigJson(url) )
                end = time.time()
                print('. Took '+ str(end - start) + ' seconds!')
            if locale['extract_strategy'] == 'quickCapsules':
                start = time.time()
                print('Processing quickCapsules from '+ country),
                saveQuickCapsules(writer, timestamp, country, fx, getNespressoQuickCapsulesJson(url) )
                end = time.time()
                print('. Took '+ str(end - start) + ' seconds!')
finally:
    f.close()
endGlobal = time.time()
globalMinutes, globalSeconds = divmod(endGlobal - startGlobal , 60)
print('All process took '+ str(globalMinutes) + ' minutes and '+ str(globalSeconds) + ' seconds!')
