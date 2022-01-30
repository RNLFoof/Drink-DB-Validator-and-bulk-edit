import collections

import requests
import json, os, re, shutil, datetime
from io import BytesIO
from PIL import Image
import copy
import time
from mf import *
import settings

cockpath = r"S:\Code\AndroidProjects\Impotent-Bartender\app\src\main\res\raw\allcocktails.json"
ingpath = r"S:\Code\AndroidProjects\Impotent-Bartender\app\src\main\res\raw\allingredients.json"
retcock = []
for x in os.listdir("sources"):
    retcock += json.load(open(os.path.join("sources", x), "rb"))
reting = {} #json.load(open(ingpath, "rb"))

# This is used to filter out what information is shown. You know for debugging. It's regex.
monitor = r"Bitters"

# Add ingredient categories
for categoryname in settings.INGREDIENT_CATEGORIES:
    #for y in ["", "Unflavored "] + [f"{z} " for z in settings.FLAVORS.keys()]:
        #toadd = IngredientInAll(y+x)
        toadd = IngredientInAll(categoryname)
        toadd.modifiable = False
        reting[categoryname] = toadd

# Add defaults to settings.FLAVORS
for flavorname, flavorinfo in settings.FLAVORS.items():
    flavorinfo.setdefault("alsoaccepts", [])

# Generate flavor mapping that also includes alsoaccepts
wordtoflavormaps = []
WordToFlavorMap = collections.namedtuple("WordToFlavorMap", ["word", "flavor"])
for flavorname, flavorinfo in settings.FLAVORS.items():
    for workingflavorname in [flavorname] + flavorinfo["alsoaccepts"]:
        wordtoflavormaps.append(WordToFlavorMap(workingflavorname, flavorname))
wordtoflavormaps.sort(key=lambda x: -len(x.word))  # Largest first

def getshouldbe(s):
    shouldbe = s.strip().title()
    while True:
        rem = shouldbe
        for x in re.finditer(r"((\b(And|Or|De|'N')\b)|('S\b))", shouldbe, flags=re.IGNORECASE):
            start = x.start(0)
            end = x.end(0)

            shouldbe = shouldbe[:start] + x.group().lower() + shouldbe[end:]

        for f,t in settings.INGREDIENT_RELPACEMENTS:
            shouldbe = re.sub(f, t, shouldbe)

        shouldbe = re.sub(r" For Colou?r$", "", shouldbe)
        shouldbe = re.sub(r"^Davinci ", "", shouldbe)
        shouldbe = re.sub(r"^Torani ", "", shouldbe)
        shouldbe = re.sub(r"^Sugar Free ", "", shouldbe)

        shouldbe = re.sub(r"^Awberry", "Strawberry", shouldbe)
        shouldbe = re.sub(r"^Awberries", "Strawberries", shouldbe)

        for regex, new in settings.INGREDIENT_ROUNDUP:
            if re.fullmatch(regex, shouldbe):
                shouldbe = new

        shouldbe = shouldbe.strip()

        vangoghless = shouldbe.replace("Van Gogh Silhouette ", "")
        vangoghless = vangoghless.replace("Van Gogh Sundance ", "")
        vangoghless = vangoghless.replace("Van Gogh ", "")
        if vangoghless in reting:
            shouldbe = vangoghless

        if rem == shouldbe:
            return shouldbe

def amimonitoring(this):
    return re.search(monitor, this, re.IGNORECASE) is not None

# old = json.load(open("allcocktailsold.json", "rb"))
images = os.listdir("images")

# This loop continues until it goes a whole rotation with no changes.
# It could probably be more efficient, but I'd rather be sure that it does everything properly by having everything in the loop.
while True:
    remcock = copy.deepcopy(retcock)
    reming = copy.deepcopy(reting)
    try:
        # Cocktail changes
        for n, i in enumerate(list(retcock)):
            # Save URL images for later use
            imgname = f"drinkimg_{re.sub(r'[^a-z0-9_]','_',i['name'].lower())}.png"
            imgnamesmall = f"drinkimg_{re.sub(r'[^a-z0-9_]','_',i['name'].lower())}_small.png"

            if imgname not in images:
                try:
                    response = requests.get(i["image"])
                    img = Image.open(BytesIO(response.content))
                    img.convert('RGB').save(f"images/{imgname}", "PNG", optimize=True)
                except Exception as e:
                    if False:
                        print(imgname)
                        print(e)

            if imgname in images and imgnamesmall not in images:
                try:
                    img = Image.open(f"images/{imgname}")
                    img.thumbnail((80, 80), 3)
                    img.convert('RGB').save(f"images/{imgnamesmall}", "PNG", optimize=True)
                except Exception as e:
                    if False:
                        print(imgnamesmall)
                        print(e)

            # Some changes that I should move to their respective sources
            if i["source"] == "Van Gogh":
                if i["name"].endswith("(Low Carb Version)"):
                    print("Removing", i["name"])
                    retcock.remove(i)

                match = re.search("(Sugar Free)(?!~)", i["name"])
                if match:
                    print(i["name"], "to")
                    i["name"] = i["name"].replace(match.group(), f"~~{match.group()}~~")
                    print(i["name"])

            elif i["source"] == "Van Gogh" and i["name"].endswith("(Low Carb Version)"):
                print("Removing", i["name"])
                retcock.remove(i)

            for y in i["ingredients"]:
                y["ingredient"] = getshouldbe(y["ingredient"])
                if y["ingredient"] == "Powdered Sugar" and i["source"] == "TheCocktailDB":
                    y["ingredient"] = "Simple Syrup"


        # Make ingredients that don't exist
        fuck = set()
        for x in retcock:
            for y in x["ingredients"]:
                if y["ingredient"] not in reting and y["ingredient"] not in fuck:
                    if amimonitoring(y["ingredient"]):
                        print(y["ingredient"], "DOESN'T FUCKING EXISWT")
                    reting[y["ingredient"]] = IngredientInAll(y["ingredient"])

        # Set default variants
        taken = set()
        otheringssorted = sorted(reting.keys(), key=lambda x: -len(x))
        for k, i in dict(reting).items():
            # What can be searched?
            # If a match is found, then it can only be a variant of the second item, or one of its variants.
            forcedvariantof = None
            for regex, forcedvariantofmaybe in settings.VARIATION_MATCHES:
                if re.search(regex, k):
                    forcedvariantof = forcedvariantofmaybe
                    forcedvariationregex = regex  # For printing
                    if amimonitoring(k):
                        print(f"{k} is going to be a variant of {otheritem} or one of its variants, because it matched {forcedvariationregex}")
                    break
            if forcedvariantof:
                otheringssorted = reting[forcedvariantof].getsubvariants(reting)
            else:
                otheringssorted = reting.keys()
            otheringssorted = sorted(otheringssorted, key=lambda x: -len(x))

            # Actually figure it out
            # Looking for matches at the start
            for otheritem in otheringssorted:
                if otheritem != k and otheritem in k and re.search(fr"\b{re.escape(otheritem)}$", k, flags=re.IGNORECASE):
                    if i.variantof != otheritem:
                        if amimonitoring(k) or amimonitoring(otheritem):
                            print(rf"Set {k} to a be a variant of {otheritem} because it matched \b{re.escape(otheritem)}$")
                    i.variantof = otheritem
                    break
            # Looking for matches anywhere
            else:
                for otheritem in otheringssorted:
                    if otheritem != k and otheritem in k and re.search(fr"\b{re.escape(otheritem)}\b", k, flags=re.IGNORECASE):
                        if i.variantof != otheritem:
                            if amimonitoring(k) or amimonitoring(otheritem):
                                print(fr"Set {k} to a be a variant of {otheritem} because it matched \b{re.escape(otheritem)}\b")
                        i.variantof = otheritem
                        break
                else:
                    # If nothing else is found, and there was a forced variant, use that
                    if forcedvariantof:
                        if i.variantof != forcedvariantof:
                            if amimonitoring(k) or amimonitoring(forcedvariantof):
                                print(f"Set {k} to a be a variant of {forcedvariantof} because nothing else was found and it matched {forcedvariationregex}")
                        i.variantof = forcedvariantof

        # Apply normalization
        for k,i in dict(reting).items():
            istart = str(i)
            if not i.modifiable:
                continue
            try:
                shouldbe = getshouldbe(k)
                if shouldbe in taken:
                    if amimonitoring(shouldbe):
                        print(f"Dupe of {shouldbe}")
                taken.add(shouldbe)
                if k != shouldbe:
                    if amimonitoring(shouldbe):
                        print(f"'{k}' should be '{shouldbe}'")

                        for x in retcock:
                            for y in x["ingredients"]:
                                if y["ingredient"] == k:
                                    print(f"{y['ingredient']} = {shouldbe}")

                    reting.setdefault(shouldbe, i)
                    del reting[k]
                    for x in retcock:
                        for y in x["ingredients"]:
                            if y["ingredient"] == k:
                                y["ingredient"] = shouldbe

                if shouldbe != i.ingredient:
                    if amimonitoring(shouldbe):
                        print(f"Internal external mismatch in {shouldbe}")
                    i.ingredient = shouldbe

            except Exception as e:
                print(f"> {istart}")
                print(f"> {i}")
                raise e

        # Variants
        # For each ingredient(i1), collect every other ingredient(i2) that has i1 as its variantof.
        for settingingname, settinginginfo in dict(reting).items():
            l = []
            for scanningingname, scanninginginfo in reting.items():
                if scanninginginfo.variantof == settingingname:
                    l.append(scanningingname)
            if l != settinginginfo.variants:
                if amimonitoring(settingingname):
                    print(f"Setting {settingingname}'s variants to {l}")
                settinginginfo.variants = l

        # Set flavors on individual ingredients
        for ingname, inginfo in dict(reting).items():
            originalingname = ingname  # Just for printing
            ingname = ingname.lower()
            originalflavors = list(inginfo.flavors)  # So we can detect changes and print them
            inginfo.flavors = []  # Reset flavors
            for map in wordtoflavormaps:
                if map.word.lower() in ingname:
                    inginfo.flavors.append(map.flavor)
                    ingname = ingname.replace(map.word.lower(), "")  # Prevent conflicts

            # Flavored if it has flavors
            inginfo.flavored = len(inginfo.flavors) != 0
            # Flavored if the entire category is flavored
            if not inginfo.flavored and inginfo.variantof in settings.FLAVORED_INGREDIENT_CATEGORIES:
                if amimonitoring(originalingname):
                    print(originalingname, "has been forced to be flavored by the settings.")
                inginfo.flavored = True
            # Show changes
            if originalflavors != inginfo.flavors:
                if amimonitoring(ingname):
                    print(f"Changed {ingname}'s flavors from {originalflavors} to {inginfo.flavors}")




        if reting == reming and retcock == remcock:
            break
        else:
            print("AGAIN")
    except Exception as e:
        print(f"OW: {e}")
        time.sleep(1)
        raise e

# Once everything is set, mark as flavored or unflavored.
# Categories require it if they contain both flavored and unflavored ingredients.
# Assuming variants have the same flavors as their parents. Freaking hope they do lol
# OI!!! There's no way to deal with two groups inside each other, I don't think. figure that out.

# This used to use settings.INGREDIENT_CATEGORIES, but I think it makes more sense to use this:
categories = []
for ingname, inginfo in dict(reting).items():
    if inginfo.variantof is None and inginfo.variants:
        categories.append(ingname)

# Init all categories with a set
categoryhastheseflavoredvalues = {}
for category in categories:
    categoryhastheseflavoredvalues[category] = set()

# Go through all items and, if relevant, track their flavored status
for inginfo in dict(reting).values():
    if inginfo.variantof in categoryhastheseflavoredvalues:
        categoryhastheseflavoredvalues[inginfo.variantof].add(inginfo.flavored)

# Now that we know what needs splitting, generate them, and transfer the references.
for categoryname in categories:
    if len(categoryhastheseflavoredvalues[categoryname]) == 2:
        bothkeys = []
        for flavored in ["Unflavored", "Flavored"]:
            # Gen
            key = f"{flavored} {categoryname}"
            bothkeys.append(key)
            toadd = IngredientInAll(key)
            toadd.modifiable = False
            toadd.variantof = categoryname  # Layer 2 down
            toadd.blocksdownwardmovement = flavored.startswith("F")  # Flavored blocks
            reting[key] = toadd
        # Transfer
        for ingredientname in reting[categoryname].variants:
            ingredient = reting[ingredientname]
            ingredient.variantof = bothkeys[ingredient.flavored]  # Layer 3 down
            reting[ingredient.variantof].variants.append(ingredientname)  # Layer 2 up
        reting[categoryname].variants = bothkeys  # Layer 1 up
        reting[categoryname].blocksdownwardmovement = True
    # Also, if there's only 1, and they're all flavored, block it off
    elif len(categoryhastheseflavoredvalues[categoryname]) == 1 and\
         list(categoryhastheseflavoredvalues[categoryname])[0]:  # Flavored?
        reting[categoryname].blocksdownwardmovement = True
        if amimonitoring(categoryname):
           print(categoryname, "blocked off")


# Count
for k,i in dict(reting).items():
    shouldbe = getshouldbe(k)
    n = 0
    for x in retcock:
        for y in x["ingredients"]:
            if y["ingredient"] == shouldbe:
                n += 1
    if n != reting[shouldbe].usecount:
        #print(f"Setting {shouldbe}'s usecount to {n}")
        reting[shouldbe].usecount = n

# Convert to dicts
for k, i in reting.items():
    reting[k] = i.todict()

# Save
with open(cockpath, "w") as f:
    json.dump(retcock, f, indent=4)
with open(ingpath, "w") as f:
    json.dump(reting, f, indent=4)
with open("results/allcocktails.json", "w") as f:
    json.dump(retcock, f, indent=4)
with open("results/allingredients.json", "w") as f:
    json.dump(reting, f, indent=4)

