import json
import re
import sqlite3

def textfactory(b):
    b = re.sub(rb"Cr.me", b"Creme", b)
    b = b.replace(b"\xe9", b"e")
    b = b.replace(b"\x92", b"'")
    b = b.replace(b"\x91", b"'")
    b = b.replace(b"\xc6", b"'")
    try:
        return b.decode("UTF-8")
    except Exception as e:
        print(b)
        raise e

cock = []
ing = {}
originalingpath = r"S:\Code\AndroidProjects\Impotent-Bartender\app\src\main\res\raw\allingredients.json"
originalings = json.load(open(originalingpath, "rb"))

conn = sqlite3.connect("vangogh.sqlite3")
conn.text_factory = textfactory
c = conn.cursor()

fuckoffs = 0
optionals = set()

for row in c.execute("SELECT * FROM recipes"):
    # print(row)
    try:

        if "Fresh Grapefruit Dipped In Sugar" in row or "Fresh Squeezed" in row or "Chilled Shot of" in row or "Shucked Oyster or Clam" in row or "Sugar Free Double Espresso Iced Mocha" in row or "Hear No Evil" in row or "Liqueur" in row:
            fuckoffs += 1
            continue

        d = {}
        d["name"] = row[1]
        if d["name"] == "Flirtini":
            d["Glass"] = "Cocktail Glass"
        else:
            try:
                d["Glass"] = re.search(r"(double )?\w+ glass", row[56]).group().title()
            except:
                pass
        d["instructions"] = (row[56] + "\n\n" + row[57]).strip()
        d["source"] = "Van Gogh"

        d["ingredients"] = []
        ingcols = row[2:56]
        for x in range(18)[::3]:
            working = ingcols[x:x+3]
            if working[0]:
                d2 = {}
                match = re.search(r"((?:\d+ )?\d+(?:/\d+)?) (\w+)", working[0])
                if match:
                    d2["quantity"] = match.group(1)
                    d2["unit"] = match.group(2)
                else:
                    match = re.search(r"(Dash|dash|Splash)( of)?", working[0])
                    d2["quantity"] = "1"
                    d2["unit"] = match.group(1).lower()
                d2["ingredient"] = (str(working[1]) + " " + str(working[2])).strip()
                d["ingredients"].append(d2)

                if d2["ingredient"] in ["Sour"]:
                    print(row)

                if d2["ingredient"] not in originalings:
                    if re.search("White de Cacao|Cherri-Suissee|Frangelica|Passoa|White Godiva|Amaretto|Remy Red|Aquavit|99 Bananas|Baileys|Nassau Royale|Liquor|Appelfest|Bols Pumpkin Smash|Brandy|Midori|Malibu|Vodka|Liqueur|151|Cider|Triple Sec|Rum|Creme de|Cream de|Schnapps|Chambord", d2["ingredient"], flags=re.IGNORECASE):
                        alc = "Yes"
                    elif re.search("Fresh Grapefruit Dipped In Sugar|Juice \(from maraschino cherry jar\)|Sweet 'n' Sour|Sweet & Sour|Juice From A Fresh Squeezed Lemon|Grenadine For Color|Grenadine Syrup for color|(Sprite \(Lemon-Lime Soda\)|mix|Creme|Flavoring|Half And Half Creme|Grenadine|Soda|Eggnog|Half and Half|Half & Half|Espresso|Juice|Nectar|Syrup|Water|Milk|Coffee|Sauce|Yogurt|Ice Cream|Chocolate Chips|Cream|Mud ?Slide Mixer)$", d2["ingredient"], flags=re.IGNORECASE):
                        alc = "No"
                    else:
                        print(">", d2["ingredient"])
                        continue
                    ing[d2["ingredient"]] = {
                        "strIngredient": d2["ingredient"],
                        "strDescription": None,
                        "strType": None,
                        "strAlcohol": alc,
                        "strABV": None
                    }
        # print(d)
        optional = []
        match = re.search(r"Garnish with(?: an)? (.+?)(\. |$)", d["instructions"].replace("Mr.", "Mr!!!"))
        if match:
            for x in re.sub(r",|\b(Floating|Type Of|^of|Serve In Double Martini Glass|and serve is silver mint julep cup|Of The Above|Several|Sugarless|Any|Topped With|Few|Melon Baller Scoop Of|Spoon Of|Drop|Piece Of Any|Heaping Teaspoon Of|Over The Rim Of Glass|Any Of The Above|Three|Fresh|and|or|,|\d-\d|\d|On A|Top With|Heaping Spoon Of|Hershey's|A|Small|Sprinkle Of|On Top)\b", ";;;",
                            match.group(1)
                                    .replace(" fresh", "")
                                    .replace("black or green olives", "black olives or green olives")
                                    .replace("red or green maraschino cherry", "red maraschino cherry or green maraschino cherry")
                                    .replace("red and yellow apple slice", "red apple slice and yellow apple slice")
                                    .replace("green or red maraschino cherry", "green maraschino cherry or red maraschino cherry")
                    , flags=re.IGNORECASE).split(";;;"):
                gonnaadd = x.strip().title()
                gonnaadd = re.sub("\.$", "", gonnaadd).strip()
                gonnaadd = re.sub("^Of ", "", gonnaadd).strip()
                if gonnaadd == "Banana Liqueur Slice":
                    gonnaadd = "Banana Slice"

                cut = re.search(r"(Peel|Half|Piece|Wedge|Slice|Chunk|Twist|Slivers|Sprig|Ball$|Stalk$|Leaf$|Cube$)(?: Of|s$)?", gonnaadd)
                if cut:
                    gonnaadd = gonnaadd.replace(cut.group(0), "").strip() + f" ({cut.group(1)})"
                if gonnaadd == "Long Orange (Twist)":
                    gonnaadd = "Orange (Long Twist)"

                gonnaadd = gonnaadd.replace("Mr!!!", "Mr.")
                if gonnaadd:
                    optional.append(gonnaadd)
                    optionals.add(gonnaadd)
                if gonnaadd in ["Of Whipped Cream", "Miniature Mr", "Green", "Serve Is Silver Mint Julep Cup", "Red", "Black", "Banana Liqueur Slice"," (Slice)", " (Sprig)"]:
                    print(match.group(0))
                    print(gonnaadd)
                    print(d["instructions"])
        d["optional"] = optional
        cock.append(d)
    except:
        fuckoffs += 1
print(ing)
print(len(originalings.keys()))
print(f"{fuckoffs} fuck offs")
print("All optionals:", str(sorted(optionals))) # .replace(",", "\n"))


with open("vangoghing.json", "w") as f:
    json.dump(ing, f, indent=4)
with open("sources/vangoghcock.json", "w") as f:
    json.dump(cock, f, indent=4)