import requests
import json, os, re, shutil, datetime
from io import BytesIO
from PIL import Image

ingpath = r"S:\Code\AndroidProjects\Impotent-Bartender\app\src\main\res\raw\allingredients.json"
reting = json.load(open(ingpath, "rb"))

print(sorted(reting.keys()))