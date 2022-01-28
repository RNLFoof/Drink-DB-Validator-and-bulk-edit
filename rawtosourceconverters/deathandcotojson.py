
from __future__ import print_function

import json
import pickle
import sys
import time
import traceback
from os import startfile

import requests
from selenium import webdriver
from selenium.webdriver import FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import csv
from datetime import datetime
import re
from ctypes import Structure, windll, c_uint, sizeof, byref

from mf import IngredientInCocktail

if not os.path.exists('stinkydata.pickle'):
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    # The ID and range of a sample spreadsheet.
    SAMPLE_SPREADSHEET_ID = '18vysHJ4EmahkaCTRCW4GqLpssZlEYjiEeLwxDD56Hns'
    chargeshot = []
    for SAMPLE_RANGE_NAME in ["Sheet1"]:#['Sheet1!A1:OD200', 'Sheet1!A201:OD479']:

        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        values = result.get('values', [])
        chargeshot += values
        #time.sleep(60)
    with open('stinkydata.pickle', 'wb') as f:
        pickle.dump(chargeshot, f)
    values = chargeshot

else:
    with open('stinkydata.pickle', 'rb') as f:
        values = pickle.load(f)

# ok anyway
print(values)

l = []
ings = values[0][7:7+378]
print(ings[-1])
print(values[0][-1])
for row in values[1:]:
    d = {}
    d["name"] = row[0]
    d["Glass"] = row[2]
    d["instructions"] = f"Okay so you take all the stinky ingredients and you [[[{row[3]}]]] them and the glass they go into is a freaking [[[{row[2]}]]]"

    currentings = []
    for n, ci in enumerate(row[7:7+378]):
        if ci:
            currentings.append({
                "quantity": " ".join(ci.split(" ")[:-1]),
                "unit": ci.split(" ")[-1],
                "ingredient": ings[n]
            })

    if row[4]:
        for blah in row[4].split(","):
            # blah = blah.strip()
            # d["instructions"] += f"\nAlso [[[{blah}]]] is listed as a Muddle/Egg/Other"
            # currentings.append({
            #     "quantity": " ".join(blah.split(" ")[:-1]),
            #     "unit": "",
            #     "ingredient": blah.split(" ")[-1]
            # })
            ing = IngredientInCocktail.createfromstring(blah)
            d["instructions"] += f"\nAlso [[[{blah}]]] is listed as a Muddle/Egg/Other"
            currentings.append(ing.getdict())

    d["ingredients"] = currentings

    d["optional"] = []
    d["source"] = "Death and Co."

    if row[5]:
        d["instructions"] += f"\nDon't forget to rinse with [[[{row[5]}]]]"
        d["optional"].append(row[5])

    if row[6]:
        d["instructions"] += f"\nAlso rim with [[[{row[6]}]]]"
        d["optional"].append(row[6])
    # print(row[0], len(row))
    # Twist and garnish
    if len(row) > 7+378 and row[7+378]:
        twist = row[7+378]
    else:
        twist = None
    if len(row) > 7+378+1 and row[7+378+1]:
        garnish = row[7+378+1]
    else:
        garnish = None

    if twist:
        twistadd = twist.replace(" Twist", "") + " (Twist)"
        d["optional"].append(twistadd)
        d["instructions"] += f"\nAlso garnish with [[[{twistadd}]]]"
    elif garnish:
        d["optional"].append(garnish)
        d["instructions"] += f"\nAlso garnish with [[[{garnish}]]]"
    l.append(d)

with open("sources/deathandcocock.json", "w") as f:
    json.dump(l, f, indent=4)