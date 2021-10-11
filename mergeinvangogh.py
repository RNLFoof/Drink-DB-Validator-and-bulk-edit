import requests
import json, os, re, shutil, datetime
from io import BytesIO
from PIL import Image

cockpath = r"S:\Code\AndroidProjects\Impotent-Bartender\app\src\main\res\raw\allcocktails.json"
ingpath = r"S:\Code\AndroidProjects\Impotent-Bartender\app\src\main\res\raw\allingredients.json"
shutil.copyfile(cockpath, r"S:/Code/Drink DB Validator and bulk edit/backups/allcocktails/"+ datetime.datetime.utcnow().strftime('%Y-%m-%d %H %M %S') +".json")
shutil.copyfile(ingpath, r"S:/Code/Drink DB Validator and bulk edit/backups/allingredients/"+ datetime.datetime.utcnow().strftime('%Y-%m-%d %H %M %S') +".json")

retcock = json.load(open(cockpath, "rb"))
reting = json.load(open(ingpath, "rb"))

vangoghcock = json.load(open("vangoghcock.json", "rb"))
vangoghing = json.load(open("vangoghing.json", "rb"))

retcock += vangoghcock
reting.update(vangoghing)

with open(cockpath, "w") as f:
    json.dump(retcock, f, indent=4)

with open(ingpath, "w") as f:
    json.dump(reting, f, indent=4)