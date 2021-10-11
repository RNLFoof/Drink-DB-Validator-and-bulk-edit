import json

cocks = json.load(open("sources/originals.json", "rb"))
for n in range(0, len(cocks))[::-1]:
    cock = cocks[n]
    if cock["source"] == "Van Gogh":
        del cocks[n]

with open("sources/originals.json", "w") as f:
    json.dump(cocks, f, indent=4)