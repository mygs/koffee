#!/usr/bin/python
import urllib
import datetime
import re
import csv
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from forex_python.converter import CurrencyRates


def getNespressoJson( url ):
    pattern='var blockConfig =(.*),\n'
    class AppURLopener(urllib.FancyURLopener):version = "Mozilla/5.0"
    req = AppURLopener().open(url)
    webpage = req.read().decode('utf-8')
    blockConfigStr = re.search(pattern, webpage)
    blockConfig = json.loads(blockConfigStr.group(1))
    return blockConfig

def saveCsv( writer, date, country, fx, json ):
    for type in json['groups']:
        for coffees in type['products']:
            id = coffees['id'].encode('utf-8')
            title = coffees['title'].encode('utf-8')
            type = coffees['type'].encode('utf-8')
            price = coffees['price']
            iconHref = coffees['iconHref'].encode('utf-8')
            coffeeStrength = coffees['coffeeStrength']
            numberOfUnits = coffees['numberOfUnits']
            #print id+"\t"+title+"\t"+type+"\t"+str(coffeeStrength)+"\t"+str(price)+"\t"+str(numberOfUnits)+"\t"+iconHref
            if numberOfUnits == 1:
                if (fx == 'BRL'):
                    preco = price
                else:
                    preco = CurrencyRates().convert(fx, 'BRL', price)

                writer.writerow( (date,country,id,title,coffeeStrength,price,preco,iconHref))
    return;

#with open('nespresso-capsules-jp_EN.json') as json_data:
#    d = json.load(json_data)
#    parseNespressoJson(d)


def readGoogleSheets(filename, sheetname):
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)
    localesheet = client.open(filename).worksheet(sheetname)
    return localesheet.get_all_records()


timestamp = datetime.date.today().strftime("%Y%m%d")
csv_file='./data/capsule-prices-'+timestamp+'.csv'

f  = open(csv_file, "wb")
try:
    writer = csv.writer(f, delimiter=';')
    writer.writerow( ('date','country','id','title','coffeeStrength','localprice','brl','iconHref') )
    for locale in readGoogleSheets('nespresso', 'locale'):
        if locale['extract_strategy'] == 'blockConfig':
                country = locale['country']
                url = locale['capsules_url']
                fx = locale['fx']
                print('Processing '+ country)
                saveCsv(writer, timestamp, country, fx, getNespressoJson(url) )
finally:
    f.close()
