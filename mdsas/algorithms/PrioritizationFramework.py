# Current context:
# (1) Location -> Weather (2) Location -> Density  (3) Tier Class ID

# Object
# {
#  'nodeName': 'node1sadf', 'location': '12.345678,98.7654321', 'IPAddress': '192.162.114.31',
#  'trustLevel': '5', 'minFrequency': '1', 'maxFrequency': '2', 'minSampleRate': '1',
#  'maxSampleRate': '2', 'nodeType': 'VT-Wireless-Registered Radar', 'mobility': 'true',
#  'status': 'INACTIVE', 'comment': '', 'userId': 'admin',
#  'fccId': '2146231f-43a0-49be-9cd4-04204d1b39e4', 'sid': 1
# }
import datetime
import json
import logging
import urllib.request
import urllib.error
from functools import lru_cache

import policies
from policies import RULE

weather_url = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline'
APIKey = "V9FLEE2X9QDASZNNCQQBVUZL5"


class Context:
    """
    Interface for the context information template that will be used by all member blocks
    """

    # cbsd_id: int
    # secondary_user_type: str
    # target_band: str
    location: str
    minFrequencyThreshold: int
    maxFrequencyThreshold: int
    mobile: bool
    # data_type: str
    # start_time: int
    # duration: int

    def __init__(self, knowledge):
        self.location = knowledge.get("location", None)
        self.minFrequencyThreshold = int(knowledge.get("minFrequency", 2.3e9))
        self.maxFrequencyThreshold = int(knowledge.get("maxFrequency", 2.4e9))

        mobility = knowledge.get("mobility", "false")
        self.mobile = True if mobility.lower() == "true" else False

    def toString(self):
        return json.dumps({
            'location': self.location,
            'minFrequencyThreshold': self.minFrequencyThreshold,
            'maxFrequencyThreshold': self.maxFrequencyThreshold,
            'mobile': self.mobile
        })


def get_priority_score(cbsd_object):
    priority_score = 0

    # Create Context Variable
    context = Context(cbsd_object)

    rule: policies.RULE = get_rule_for_band(context)

    # Calculate Scores:
    weather = get_weather_for_location(context.location)
    weather_score = rule.weather.index(weather) + 1
    mobility_score = 1 if context.mobile else 0

    # Sum Scores:
    priority_score += weather_score + mobility_score

    all_scores = f"Weather Score: {weather_score}, " \
                 f"Mobility Score: {mobility_score}. " \
                 f"Priority Score: {priority_score}"
    logging.warning(all_scores)
    return priority_score


def get_rule_for_band(context) -> policies.RULE:
    min, max = int(context.minFrequencyThreshold / 1e6), int(context.maxFrequencyThreshold / 1e6)

    for name, band in policies.BANDS.items():
        if band["min-op-fr"] == min or band["max-op-fr"] == max or \
                band["min-op-fr"] <= min < max <= band["max-op-fr"]:
            rule: RULE = band['rule']

            if rule:
                return policies.RULES[rule]
            else:
                return policies.RULES['default']

    logging.warning("Could not match the provided frequency range to a band. Context:" + context.toString())
    return policies.RULES['default']


@lru_cache(maxsize=20)
def get_weather_for_location(location):
    lat, long = location.split(',')
    url = f"{weather_url}/{lat}%2C{long}/today?unitGroup=metric" \
          f"&key={APIKey}&contentType=json"

    jsonData = None
    try:
        ResultBytes = urllib.request.urlopen(url)
        logging.warning("Fetched Results at: " + str(datetime.datetime.now()))

        # Parse the results as JSON
        jsonData = json.loads(ResultBytes.read())
    except Exception as e:
        logging.error(e)

    if not jsonData or 'currentConditions' not in jsonData or "conditions" not in jsonData['currentConditions']:
        raise Exception('Current data not available')

    currentConditions = jsonData['currentConditions']
    currentWeather = currentConditions.get("conditions").lower().strip()

    if currentWeather == 'clear':
        return "clear"
    elif currentWeather == 'overcast':
        return "overcast"
    elif ',' not in currentWeather and 'cloudy' in currentWeather:
        return 'cloudy'
    elif "rain" in currentWeather:
        return "rain"
    elif "snow" in currentWeather:
        return "snow"
    else:
        print(f"Unidentified Weather: {currentWeather}")
        print("Corresponding policy not found for this type of weather. Using default.")
        return "clear"
