import re

def strtonum(s):
    s = s.strip()
    # Int
    if re.match(r"^\d+$", s):
        return int(s)

    # Float
    if re.match(r"^(\.|\d)+$", s):
        return float(s)

    # 1/2
    match = re.match(r"^(\d+)/(\d+)$", s)
    if match:
        return int(match.group(1)) / int(match.group(2))

    # 1 1/2
    match = re.match(r"^(\d+) (\d+)/(\d+)$", s)
    if match:
        return int(match.group(1)) + int(match.group(2)) / int(match.group(3))

    raise Exception(f"Couldn't parse {s} as a number.")

class IngredientInCocktail:
    def __init__(self, high, low, unit, ingredient):
        self.high = high
        self.low = low
        self.unit = unit
        self.ingredient = ingredient

    @classmethod
    def createfromstring(cls, s):
        s = s.strip()
        # Maybe add a quantity
        if re.match("small pinch|pinch|dash", s.lower()):
            s = "1 " + s
        # Get quantity
        quantitymatch = re.match(r"(\d| to | or |/| )+", s)
        if not quantitymatch:
            raise Exception(f"No quantity found in {s}")
        quantitystr = quantitymatch.group()
        s = s[len(quantitystr):].strip()
        quantitystr = quantitystr.replace(" to ", "-")
        quantitystr = quantitystr.replace(" or ", "-")
        if "-" in quantitystr:
            low = strtonum(quantitystr.split("-")[0])
            high = strtonum(quantitystr.split("-")[1])
        else:
            low = strtonum(quantitystr)
            high = strtonum(quantitystr)

        # Get unit
        unitmatch = re.match("(oz|ml|dl|pinch)( of)?", s.lower())
        if unitmatch:
            unit = unitmatch.group(1)
            s = s[len(unit):].strip()
        else:
            unit = ""

        # Ingredient
        ingredient = s

        # Return
        return IngredientInCocktail(high, low, unit, ingredient)

    def getquantity(self):
        if self.low == self.high:
            return self.high
        return round((self.high + self.low)/2, 3)

    def getdict(self):
        return {
            "quantity": str(self.getquantity()),
            "unit": self.unit,
            "ingredient": self.ingredient
        }

class IngredientInAll():
    def __init__(self, ingredient):
        self.ingredient = ingredient
        self.alcoholic = False
        self.abv = 0
        self.variantof = None
        self.usecount = 0
        self.variants = []
        self.modifiable = True  # Set to false when it's a pre-determined category, allowing, for example, "Bitters" to be
                                # changed to "Angostura Bitters" without getting rid of the Bitters category
        self.flavored = False
        self.blocksdownwardmovement = False  # Used if lowering to this point makes no sense, ex. Flavored Vodka


    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return self.todict() == other.todict()

    def getsubvariants(self, ingdict, buildup=None):
        if not buildup:
            buildup = set()
        for variant in self.variants:
            if variant not in buildup:
                buildup.add(variant)
                ingdict[variant].getsubvariants(ingdict, buildup=buildup)
        return buildup

    def todict(self):
        return {
            "strIngredient": self.ingredient,
            "strAlcohol": self.alcoholic,
            "strABV": self.abv,
            "variantOf": self.variantof,
            "useCount": self.usecount,
            "variants": self.variants,
            # "flavored": self.flavored, # The app doesn't use this and it can be removed
            "blocksDownwardMovement": self.blocksdownwardmovement,
        }