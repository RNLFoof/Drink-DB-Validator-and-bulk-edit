# Adds to the ingredient list for the purpose of having other shit in it.
INGREDIENT_CATEGORIES = [
    "Bitters",
    "Chartreuse",
    "Curacao Liqueur",
    "Juice",
    "Liqueur",
    "Sambuca",
    "Nectar",
    "Soda",
    "Amaro",
    "Dry Gin",
    "London Dry Gin",
    "Syrup",
]

# Partial string supstitutions.
INGREDIENT_RELPACEMENTS = [
    # Accents are removed because it's way easier to remove them than to add them back
    ("à|ä", "a"),
    ("ç", "c"),
    ("é|ê|ë|è", "e"),
    (r"\bCream de\b", "Creme de"),
    (r"\bTrader's Vic\b", "Trader Vic's"),
    (r"ies\b", "y"),
    (r"\b('n'|&)\b", "and"),
]

# Used to convert less specific ingredient names to more specific ones, so that ingredients under different names are
# treated as the same.
# More complex is picked instead of less complex because the more words there are the easier it is to find varaints.
# Regex, then, if it FULL matches, it becomes the second item.
INGREDIENT_ROUNDUP = [
    # ('Van Gogh Silhouette Liqueur', 'Vanilla Liqueur'),
    ("(Amaretto|Almond) Liq.*", "Amaretto Almond Liqueur"),
    ("99 Bananas.*", "99 Bananas Banana Liqueur"),
    ("Bailey'?s( Irish Cream)?", "Bailey's Irish Cream Liqueur"),
    ("Galliano.*", "Galliano Vanilla Liqueur"),
    ("Grand Marnier.*", "Grand Marnier Liqueur"),
    ("Grenadine Sy.* Liq.*|.*or Grenadine Syrup", "Grenadine Syrup"),
    ("Half[- ](and|&)[- ]Half Cre.*", "Half and Half Cream"),
    ("Honeydew Liqueur", "Honeydew Melon Liqueur"),
    ("Juice From A Fresh Squeezed Lemon", "Lemon Juice"),
    ("Whisky", "Whiskey"),
    ("Komet Liqueur|Das Komet Liqueur", "Das Komet Vanilla Liqueur"),
    ("Godiva Liqueur", "Godiva Chocolate Liqueur"),
    ("Creme de Banana", "Creme de Banane"),
    ('151|Bacardi 151', 'Bacardi 151 Rum'),
    ('7-Up (Lemon-Lime Soda)|7-Up', "7-Up Lemon-Lime Soda"),
    ('Bitters', 'Angostura Bitters'),
    ('Cheery Liqueur', 'Cherry Liqueur'),
    ('Irish Cream|Irish Cream|Irish Creme Liqueur', 'Irish Cream Liqueur'),
    ('Jagermeister|Jagermeister|Jägermeister', "Jagermeister Liqueur"),
    ('Kahlua|Kahlua Liqueur', "Kahlua Coffee Liqueur"),
    ('Macadamia Liqueur', 'Macadamia Nut Liqueur'),
    ('Malibu', 'Malibu Rum'),
    ('Midori', "Midori Melon Liqueur"),
    ('Mud Slide Mixer', 'Mudslide Mixer'),
    ('Nassau Royale', 'Nassau Royale Liqueur'),
    ('Orange Curacao', 'Orange Curacao Liqueur'),
    ('Sambuca', 'Sambuca Liqueur'),
    ('Hot Damn', 'Hot Damn Cinnamon Schnapps Liqueur'),
    ('Sirup of Roses', 'Rose Syrup'),
    ('Sour Appel Liqueur', 'Sour Apple Liqueur'),
    ('Southern Comfort', 'Southern Comfort Liqueur'),
    ('Sprite (Lemon-Lime Soda)|Sprite', "Sprite Lemon-Lime Soda"),
    ('Sugar Syrup', 'Simple Syrup'),
    ('White Creme de Menthe', 'White Creme de Menthe Liqueur'),
    ('Wild Turkey', 'Wild Turkey Bourbon'),
    ('Sweet and Sour', 'Sweet and Sour Mix'),
    ('Liquor 43', 'Liquor 43 Liquor'),
    ('St-Germain|St. Germain', 'St. Germain Elderflower Liqueur'),
    ('Bols Pumpkin Smash', 'Bols Pumpkin Smash Pumpkin Spice Liqueur'), #  I think these two might be the same thing, and the name changed?
    ('Bols Pumpkin Spice', 'Bols Pumpkin Spice Pumpkin Spice Liqueur'),
]

# If a match is found, then it can only be a variant of the second item, or one of its variants.
VARIATION_MATCHES = [
    (r"\b(Curacao Liqueur|Triple Sec|Grand Marnier)\b", "Orange Liqueur"),
    (r"\bAbsolut\b", "Vodka"),
    (r"\bBourbon\b", "Whiskey"),
    (r"\bCognac\b", "Brandy"),
    (r"\bCreme de\b", "Liqueur"),
    (r"\bIPA\b", "Beer"),
    (r"\bLager\b", "Beer"),
    (r"\bPisco\b", "Brandy"),
    (r"\bRoot Beer\b", "Soda"),
    (r"\bBitter Lemon\b", "Soda"),
    (r"\bRye\b", "Whiskey"),
    (r"\bSchnapps\b", "Liqueur"),
    (r"\bScotch\b", "Whiskey"),
    (r"\bTequila\b", "Mezcal"),
]

# If any match, it, and all subitems, are alcoholic.
ALCOHOLIC_MATCHES = [
    r"\bBeer\b",
    r"\bCognac\b",
    r"\bGin\b",
    r"\bLiqueur\b",
    r"\bMezcal\b",
    r"\bRum\b",
    r"\bVodka\b",
    r"\bWhiskey\b",
]

# Used to categorize.
FLAVORS = {
    "Apple": {},
    "Caramel": {},
    "Chocolate": {},
    "Blackberry": {},
    "Blueberry": {},
    "Cherry": {},
    "Cucumber": {},
    "Grape": {},
    "Lemon": {},
    "Lime": {},
    "Melon": {},
    "Orange": {},
    "Pineapple": {},
    "Raspberry": {},
    "Strawberry": {},
}