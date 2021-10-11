import os
import re
for x in os.listdir("images"):
    os.rename(f"images/{x}", f"images/drinkimg_{re.sub(r'[^a-z0-9_]','_',x.lower()[:-4])}.png")