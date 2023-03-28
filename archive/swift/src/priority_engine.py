import json
import urllib.request
import urllib.error

import pandas as pd
from functools import lru_cache
from src import policies
from src.policies import RULE


class PriorityEngine:
    context = None
    weather_url = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline'
    locations = []

    def __init__(self):
        with open("weatherapi.key", 'r+') as infile:
            self.ApiKey = infile.read().strip()

    @lru_cache(maxsize=20)
    def get_weather_for_location(self, location):
        lat, long = location.split(',')
        weather_url = f"{self.weather_url}/{lat}%2C{long}/today?unitGroup=metric" \
                      f"&key={self.ApiKey}&contentType=json"

        jsonData = None
        try:
            ResultBytes = urllib.request.urlopen(weather_url)
            # Parse the results as JSON
            jsonData = json.loads(ResultBytes.read())
        except Exception as e:
            print(e)

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

    @staticmethod
    def get_rule_for_band(band) -> policies.RULE:
        rule: RULE = policies.BANDS[band]['rule']

        if rule:
            return policies.RULES[rule]
        else:
            return policies.RULES['default']

    @lru_cache(maxsize=20)
    def get_density_of_location(self, location):
        if location in self.locations:
            location_score = self.locations[location]
        else:
            location_score = 0

        return location_score

    def calculate_score(self, row, rule: RULE):
        user_score = rule.user.index(row["secondary_user_type"]) + 1
        data_type_score = rule.traffic.index(row["data_type"]) + 1

        # Generate weather score
        weather_score = rule.weather.index(self.get_weather_for_location(row["location"])) + 1

        # Generate density distribution score
        location_score = self.get_density_of_location(row['location'])

        return {
            "user_score": user_score,
            "data_type_score": data_type_score,
            "weather_score": weather_score,
            "location_score": location_score,
            "score": sum([user_score, data_type_score, weather_score, location_score])
        }

    def get_context(self):
        return self.context

    def load_context_from_core(self, context: pd.DataFrame):
        self.context = context
        self.locations = context.groupby(['location']).size().to_dict()

    def generate_scores(self):
        block_size = len(self.context.index)//10
        self.locations = {k: v for k, v in sorted(self.locations.items(), key=lambda item: item[1])}

        for index, row in self.context.iterrows():
            if (index + 1) % block_size == 0:
                print("-", end="")

            band = row['target_band']
            rule: policies.RULE = self.get_rule_for_band(band)

            row['min_freq'] = policies.BANDS[band]["min-op-fr"]
            row['max_freq'] = policies.BANDS[band]["max-op-fr"]
            scores = self.calculate_score(row, rule)

            self.context.at[index, 'min_freq'] = row['min_freq']
            self.context.at[index, 'max_freq'] = row['max_freq']

            self.context.at[index, "user_priority"] = scores["user_score"]
            self.context.at[index, "traffic_priority"] = scores["data_type_score"]
            self.context.at[index, "fading_priority"] = scores["weather_score"]
            self.context.at[index, "density_priority"] = scores["location_score"]
            self.context.at[index, 'overall_priority'] = scores["score"]

        print("\nScore Generation Complete")
