import requests
import json, os, re, shutil, datetime
from io import BytesIO
from PIL import Image
import copy
import time

print("Yes = go")
makechanges = input() == "Yes"

cockpath = r"S:\Code\AndroidProjects\Impotent-Bartender\app\src\main\res\raw\allcocktails.json"
ingpath = r"S:\Code\AndroidProjects\Impotent-Bartender\app\src\main\res\raw\allingredients.json"
if makechanges:
    shutil.copyfile(cockpath, r"S:/Code/Drink DB Validator and bulk edit/backups/allcocktails/"+ datetime.datetime.utcnow().strftime('%Y-%m-%d %H %M %S') +".json")
    shutil.copyfile(ingpath, r"S:/Code/Drink DB Validator and bulk edit/backups/allingredients/"+ datetime.datetime.utcnow().strftime('%Y-%m-%d %H %M %S') +".json")
retcock = []
for x in os.listdir("sources"):
    retcock += json.load(open(os.path.join("sources", x), "rb"))
reting = json.load(open(ingpath, "rb"))


def getshouldbe(s):
    shouldbe = s.strip().title()
    while True:
        rem = shouldbe
        for x in re.finditer(r"((\b(And|Or|De|'N')\b)|('S\b))", shouldbe, flags=re.IGNORECASE):
            start = x.start(0)
            end = x.end(0)

            shouldbe = shouldbe[:start] + x.group().lower() + shouldbe[end:]

        shouldbe = re.sub(r" For Colou?r$", "", shouldbe)
        shouldbe = re.sub(r"^Davinci ", "", shouldbe)
        shouldbe = re.sub(r"^Torani ", "", shouldbe)
        shouldbe = re.sub(r"^Sugar Free ", "", shouldbe)

        shouldbe = re.sub(r"^Awberry", "Strawberry", shouldbe)
        shouldbe = re.sub(r"^Awberries", "Strawberries", shouldbe)

        for regex, new in conversion:
            if re.fullmatch(regex, shouldbe):
                shouldbe = new

        if shouldbe.startswith("Creme de") and shouldbe.endswith(" Liqueur"):
            shouldbe = shouldbe.replace(" Liqueur", "")

        shouldbe = shouldbe.strip()

        vangoghless = shouldbe.replace("Van Gogh Silhouette ", "")
        vangoghless = vangoghless.replace("Van Gogh Sundance ", "")
        vangoghless = vangoghless.replace("Van Gogh ", "")
        if vangoghless in reting:
            shouldbe = vangoghless

        if rem == shouldbe:
            return shouldbe

conversion = [
    ("99 Bananas.*", "99 Bananas Liqueur"),
    ("(Amaretto|Almond) Liq.*", "Amaretto"),
    ("Bailey'?s( Irish Cream)?", "Bailey's Irish Cream"),
    ("Galliano Liq.*", "Galliano"),
    ("Grand Marnier Liq.*", "Grand Marnier"),
    ("Grenadine Sy.* Liq.*|.*or Grenadine Syrup", "Grenadine"),
    ("Half[- ](and|&)[- ]Half Cre.*", "Half and Half Cream"),
    ("Honeydew Melon Liqueur", "Honeydew Liqueur"),
    ('Irish Cream|Irish Cream Liqueur|Irish Creme Liqueur', 'Irish Cream'),
    ('Jagermeister|Jagermeister Liqueur|Jägermeister', "Jagermeister"),
    ("Juice From A Fresh Squeezed Lemon", "Lemon Juice"),
    ('Kahlua Coffee Liqueur|Kahlua Liqueur', "Kahlua"),
    ('Macadamia Nut Liqueur', 'Macadamia Liqueur'),
    ('Malibu', 'Malibu Rum'),
    ('Midori', "Midori Melon Liqueur"),
    ('Mud Slide Mixer', 'Mudslide Mixer'),
    ('Nassau Royale', 'Nassau Royale Liqueur'),
    ('Orange Curacao', 'Orange Curacao Liqueur'),
    ('Sour Appel Liqueur', 'Sour Apple Liqueur'),
    ('Southern Comfort', 'Southern Comfort Liqueur'),
    ('Sprite (Lemon-Lime Soda)', "Sprite"),
    ("Whisky", "Whiskey"),
    ('White Creme de Menthe', 'White Creme de Menthe Liqueur'),
    ('Sugar Syrup', 'Simple Syrup'),
    # ('Van Gogh Silhouette Liqueur', 'Vanilla Liqueur'),
    ('Sambuca', 'Sambuca Liqueur'),
    ('Cheery Liqueur', 'Cherry Liqueur'),
    ('Cheery Liqueur', 'Liqueur'),
]

# old = json.load(open("allcocktailsold.json", "rb"))
images = os.listdir("images")
while True:
    remcock = copy.deepcopy(retcock)
    reming = copy.deepcopy(reting)


    try:



        for n, i in enumerate(list(retcock)):

            imgname = f"drinkimg_{re.sub(r'[^a-z0-9_]','_',i['name'].lower())}.png"
            imgnamesmall = f"drinkimg_{re.sub(r'[^a-z0-9_]','_',i['name'].lower())}_small.png"
            # if "image" not in i and "strDrinkThumb" in old[i['name']]:
            #    i["image"] = old[i['name']]["strDrinkThumb"]

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

            # i.setdefault("source", "TheCocktailDB")

            for y in i["ingredients"]:
                y["ingredient"] = getshouldbe(y["ingredient"])
                if y["ingredient"] == "Powdered Sugar" and i["source"] == "TheCocktailDB":
                    y["ingredient"] = "Simple Syrup"


        # Make ingredients that don't exist
        fuck = set()
        for x in retcock:
            for y in x["ingredients"]:
                if y["ingredient"] not in reting and y["ingredient"] not in fuck:
                    print(y["ingredient"], "DOESN'T FUCKING EXISWT")
                    reting[y["ingredient"]] = {
                        "strIngredient": y["ingredient"],
                        "strAlcohol": None,
                        "strABV": None
                    }

        taken = set()
        for k,i in dict(reting).items():
            i.setdefault("variantOf", None)
            if i["variantOf"] == None:
                if k.endswith("Syrup") and k != "Syrup":
                    i["variantOf"] = "Syrup"
                    print(f"Set {k} to a be a variant of Syrup")
                elif k.endswith("Liqueur") and k != "Liqueur":
                    i["variantOf"] = "Liqueur"
                    print(f"Set {k} to a be a variant of Liqueur")
                elif k.endswith("Juice") and k != "Juice":
                    i["variantOf"] = "Juice"
                    print(f"Set {k} to a be a variant of Juice")
                elif "Schnapps" in k and k.replace("Schnapps", "Liqueur") in reting:
                    i["variantOf"] = k.replace("Schnapps", "Liqueur")
                    print(f"Set {k} to a be a variant of " + k.replace("Schnapps", "Liqueur"))
                elif k.endswith("Schnapps"):
                    i["variantOf"] = "Liqueur"
                    print(f"Set {k} to a be a variant of Liqueur")
            # if k.endswith("Juice") and k != "Juice" and i["variantOf"] == None:
            #     i["variantOf"] = "Juice"
            #     print(f"Set {k} to a be a variant of Juice")
            # if k.endswith("Liqueur") and k != "Liqueur" and i["variantOf"] == None:
            #     i["variantOf"] = "Liqueur"
            #     print(f"Set {k} to a be a variant of Liqueur")

        for k,i in dict(reting).items():
            istart = str(i)
            try:
                shouldbe = getshouldbe(k)
                if shouldbe in taken:
                    print(f"Dupe of {shouldbe}")
                taken.add(shouldbe)
                if k != shouldbe:
                    print(f"'{k}' should be '{shouldbe}'")

                    for x in retcock:
                        for y in x["ingredients"]:
                            if y["ingredient"] == k:
                                print(f"{y['ingredient']} = {shouldbe}")

                    if makechanges:
                        reting.setdefault(shouldbe, i)
                        del reting[k]
                        for x in retcock:
                            for y in x["ingredients"]:
                                if y["ingredient"] == k:
                                    y["ingredient"] = shouldbe

                if shouldbe != i["strIngredient"]:
                    print(f"Internal external mismatch in {shouldbe}")
                    if makechanges:
                        i["strIngredient"] = shouldbe

            except Exception as e:
                print(f"> {istart}")
                print(f"> {i}")
                raise e

            # Count
            reting[shouldbe].setdefault("useCount", 0)
            n = 0
            for x in retcock:
                for y in x["ingredients"]:
                    if y["ingredient"] == shouldbe:
                        n += 1
            if n != reting[shouldbe]["useCount"]:
                print(f"Setting {shouldbe}'s usecount to {n}")
                reting[shouldbe]["useCount"] = n

            # Variants
            reting[shouldbe].setdefault("variants", [])
            l = []
            for k,i in reting.items():
                if i["variantOf"] == shouldbe:
                    l.append(k)
            if l != reting[shouldbe]["variants"]:
                print(f"Setting {shouldbe}'s variants to {l}")
                reting[shouldbe]["variants"] = l




        if reting == reming and retcock == remcock:
            break
        else:
            print("AGAIN")
    except Exception as e:
        print(f"OW: {e}")
        time.sleep(1)

if makechanges:
    with open(cockpath, "w") as f:
        json.dump(retcock, f, indent=4)

    with open(ingpath, "w") as f:
        json.dump(reting, f, indent=4)

