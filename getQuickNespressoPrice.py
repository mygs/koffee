#!/usr/bin/python
import urllib
import httplib
import datetime
import re
import csv
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from forex_python.converter import CurrencyRates


#type:"POST",contentType:"application/json",dataType:"json",data:DTOparametres
URL='https://www.nespresso.com/cn/en/getQuickCapsules/original'

h = httplib.HTTPConnection(URL)

headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
h.request('POST', '/getQuickCapsules/original', data, headers)

r = h.getresponse()

print (r.read())
