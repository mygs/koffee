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
from tqdm import tqdm
from oauth2client.service_account import ServiceAccountCredentials
from forex_python.converter import CurrencyRates

def getAllRecordsFromGoogleSheets(filename, sheetname):
    # use creds to create a client to interact with the Google Drive API
    SCOPE = ['https://spreadsheets.google.com/feeds']
    CREDS = ServiceAccountCredentials.from_json_keyfile_name('../client_secret.json', SCOPE)
    client = gspread.authorize(CREDS)
    localesheet = client.open(filename).worksheet(sheetname)
    return localesheet.get_all_records()

def getFXcache():
    fxcache = {}
    forexList = getAllRecordsFromGoogleSheets('nespresso', 'forex_test')
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
    pbar.close()
    return fxcache


print ('python version '+platform.python_version())
os.chdir(sys.path[0]) # change working directory to script directory

fxcache = getFXcache()
