import json
import random

data = {}
for x in range(10000):
    value = random.randint(0, 1)
    command = "normalSpectrum"
    if value > 0:
        command = "createPu"
    t = float((x/10.0) + 2)
    data[str(t)] = [command]
with open('json_test.json', 'w') as outfile:
    json.dump(data, outfile, sort_keys=True)