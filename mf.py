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

class Ingredient:
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
        return Ingredient(high, low, unit, ingredient)

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