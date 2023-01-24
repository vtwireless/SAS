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


class Score:
    """
    Interface for maintaining all types of score
    """
    weather_score: int
    mobility_score: int
    context: Context
    rule: RULE

    __score: int = 0

    def __init__(self, context: Context):
        self.weather_score = 0
        self.mobility_score = 0

        self.context = context
        self.rule = self.get_rule_for_band()

        self.__score = 0

    def calculate(self):
        self.calculate_weather_score()
        self.calculate_mobility_score()

    def get(self) -> int:
        return self.__score

    def get_rule_for_band(self) -> policies.RULE:
        min, max = int(self.context.minFrequencyThreshold / 1e6), int(self.context.maxFrequencyThreshold / 1e6)

        for name, band in policies.BANDS.items():
            if band["min-op-fr"] == min or band["max-op-fr"] == max or \
                    band["min-op-fr"] <= min < max <= band["max-op-fr"]:
                rule: RULE = band['rule']

                if rule:
                    return policies.RULES[rule]
                else:
                    break

        logging.warning("Could not match the provided frequency range to a band. Context:" + self.context.toString())
        return policies.RULES['default']

    @lru_cache(maxsize=20)
    def get_weather_for_location(self):
        lat, long = self.context.location.split(',')
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
            logging.warning(f"Unidentified Weather: {currentWeather}. Corresponding policy not found for this type of "
                            f"weather. Using default settings.")
            return "clear"

    def toString(self):
        return json.dumps({
            "Weather Score": self.weather_score,
            "Mobility Score": self.mobility_score,
            "Priority Score": self.__score
        })

    def calculate_weather_score(self):
        weather = self.get_weather_for_location()
        self.weather_score = self.rule.weather.index(weather) + 1

    def calculate_mobility_score(self):
        self.mobility_score = 1 if self.context.mobile else 0


class Engine:
    @staticmethod
    def get_priority_score(cbsd_object) -> int:
        # Create Context Variable
        context = Context(cbsd_object)

        score = Score(context)
        score.calculate()

        logging.info(score.toString())
        return score.get()
