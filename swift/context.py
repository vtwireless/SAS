import json
import urllib.request
import urllib.error
import sys


class context:
    """
    # print(json.dumps(jsonData))

    {
        "queryCost": 1,
        "latitude": 37.2296,
        "longitude": -80.4139,
        "resolvedAddress": "37.2296,-80.4139",
        "address": "37.2296,-80.4139",
        "timezone": "America/New_York",
        "tzoffset": -5.0,
        "days": [
            {
                "datetime": "2020-12-15",
                "datetimeEpoch": 1608008400,
                "tempmax": 40.0,
                "tempmin": 24.3,
                "temp": 31.6,
                "feelslikemax": 40.0,
                "feelslikemin": 22.0,
                "feelslike": 28.4,
                "dew": 26.3,
                "humidity": 81.68,
                "precip": 0.0,
                "precipprob": null,
                "precipcover": 0.0,
                "preciptype": null,
                "snow": 0.0,
                "snowdepth": 0.0,
                "windgust": 16.1,
                "windspeed": 9.2,
                "winddir": 151.3,
                "pressure": 1025.6,
                "cloudcover": 0.0,
                "visibility": 9.9,
                "solarradiation": 216.6,
                "solarenergy": 9.4,
                "uvindex": 4.0,
                "sunrise": "07:28:45",
                "sunriseEpoch": 1608035325,
                "sunset": "17:05:29",
                "sunsetEpoch": 1608069929,
                "moonphase": 0.0,
                "conditions": "Clear",
                "description": "Clear conditions throughout the day.",
                "icon": "clear-day",
                "stations": [
                    "72411013741",
                    "0450W",
                    "KBCB",
                    "72411613868",
                    "0408W",
                    "KROA",
                    "KPSK",
                    "72411353881"
                ],
                "source": "obs"
            }
        ],
        "stations": {
            "72411013741": {
                "distance": 40153.0,
                "latitude": 37.317,
                "longitude": -79.974,
                "useCount": 0,
                "id": "72411013741",
                "name": "ROANOKE INTERNATIONAL AIRPORT, VA US",
                "quality": 100,
                "contribution": 0.0
            },
            "0450W": {
                "distance": 14958.0,
                "latitude": 37.196,
                "longitude": -80.577,
                "useCount": 0,
                "id": "0450W",
                "name": "VT Kentland Farm VA US WEATHERSTEM",
                "quality": 0,
                "contribution": 0.0
            },
            "KBCB": {
                "distance": 1198.0,
                "latitude": 37.22,
                "longitude": -80.42,
                "useCount": 0,
                "id": "KBCB",
                "name": "KBCB",
                "quality": 100,
                "contribution": 0.0
            },
            "72411613868": {
                "distance": 26188.0,
                "latitude": 37.133,
                "longitude": -80.683,
                "useCount": 0,
                "id": "72411613868",
                "name": "PULASKI, VA US",
                "quality": 89,
                "contribution": 0.0
            },
            "0408W": {
                "distance": 1198.0,
                "latitude": 37.22,
                "longitude": -80.419,
                "useCount": 0,
                "id": "0408W",
                "name": "Virginia Tech VA US WEATHERSTEM",
                "quality": 0,
                "contribution": 0.0
            },
            "KROA": {
                "distance": 40589.0,
                "latitude": 37.32,
                "longitude": -79.97,
                "useCount": 0,
                "id": "KROA",
                "name": "KROA",
                "quality": 100,
                "contribution": 0.0
            },
            "KPSK": {
                "distance": 26076.0,
                "latitude": 37.13,
                "longitude": -80.68,
                "useCount": 0,
                "id": "KPSK",
                "name": "KPSK",
                "quality": 89,
                "contribution": 0.0
            },
            "72411353881": {
                "distance": 2519.0,
                "latitude": 37.208,
                "longitude": -80.408,
                "useCount": 0,
                "id": "72411353881",
                "name": "BLACKSBURG VIRGINIA TECH AIRPORT, VA US",
                "quality": 100,
                "contribution": 0.0
            }
        },
        "currentConditions": {
            "datetime": "13:00:00",
            "datetimeEpoch": 1608055200,
            "temp": 37.1,
            "feelslike": 32.5,
            "humidity": 67.7,
            "dew": 27.4,
            "precip": 0.0,
            "precipprob": 0.0,
            "snow": 0.0,
            "snowdepth": 0.0,
            "preciptype": null,
            "windgust": null,
            "windspeed": 5.8,
            "winddir": 90.0,
            "pressure": 1026.5,
            "visibility": 9.9,
            "cloudcover": 0.0,
            "solarradiation": 400.0,
            "solarenergy": 1.4,
            "uvindex": 4.0,
            "conditions": "Clear",
            "icon": "clear-day",
            "stations": [
                "72411013741",
                "KBCB",
                "72411613868",
                "KROA",
                "KPSK",
                "72411353881"
            ],
            "sunrise": "07:28:45",
            "sunriseEpoch": 1608035325,
            "sunset": "17:05:29",
            "sunsetEpoch": 1608069929,
            "moonphase": 0.01
        }
    }

    """

    BaseURL = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline'

    def __init__(self):
        with open("weatherapi.key", 'r+') as infile:
            self.ApiKey = infile.read().strip()

        # UnitGroup sets the units of the output - us or metric
        self.UnitGroup = 'us'
        self.ContentType = 'json'
        self.OutputSection = 'current%2Cevents'

    def queryBuilder(self, currentDate, latitude, longitude):
        url = f"{self.BaseURL}/{latitude}%2C{longitude}/{currentDate}?unitGroup={self.UnitGroup}" \
              f"&include={self.OutputSection}&key={self.ApiKey}&contentType={self.ContentType}"

        return url

    def scrapeWeatherForLocation(self, currentTime, latitude, longitude, aggregate=False, debug=False):
        jsonData = None

        try:
            ResultBytes = urllib.request.urlopen(
                self.queryBuilder(currentTime, latitude, longitude)
            )

            # Parse the results as JSON
            jsonData = json.loads(ResultBytes.read())

        except Exception as e:
            print(e)

        if 'currentConditions' not in jsonData:
            raise Exception('Current data not available')

        currentWeather = jsonData['currentConditions']
        if aggregate:
            currentWeather = jsonData['days'][0]

        returnable = {
            "temperature": currentWeather['temp'],
            "humidity": currentWeather["humidity"],
            "precipitation": currentWeather['precip'],
            'windspeed': currentWeather['windspeed'],
            'pressure': currentWeather['pressure'],
            'visibility': currentWeather['visibility'],
            'weather': currentWeather['conditions'],
            'cloudcover': currentWeather['cloudcover']
        }

        if debug:
            return jsonData

        return returnable


if __name__ == '__main__':
    current_time, lat, long = '2022-09-25T20:31:00', "37.2296", "-80.4139"
    # current_time = "today"

    contextEngine = context()
    weather = contextEngine.scrapeWeatherForLocation(current_time, lat, long)
    print("\n\n", json.dumps(weather, indent=4))
    # with open('context.json', "w+") as outfile:
    #     json.dump(weather, outfile, indent=4)


