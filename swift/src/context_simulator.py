import random
import pandas
from src import policies


class ContextSimulator:
    user_types, weather_types, density_types, traffic_types, bands = None, None, None, None, None
    locations = [
        "37.227279,-80.421665", "37.231585,-80.416258", "37.211525,-80.445081"
    ]

    def __init__(self, outfile, number_of_users):
        self.outfile = outfile
        self.environment = []

        # Experiment
        self.number_of_users = number_of_users
        self.get_constants()

    def get_constants(self):
        self.user_types = policies.USER_TYPE
        self.weather_types = policies.WEATHER
        self.density_types = policies.DENSITY
        self.traffic_types = policies.TRAFFIC
        self.bands = policies.BANDS

    def create_environment(self):
        all_bands = [band for band in self.bands]
        for i in range(self.number_of_users):
            band = random.choice(all_bands)
            duration = random.randint(5, 10)
            time = i + random.randint(1, duration)

            self.environment.append({
                "cbsd_id": 1000 + i + 1,
                "secondary_user_type": random.choice(self.user_types),
                "target_band": band,
                # "freq_min": self.bands[band]['min-op-fr'],
                # "freq_max": self.bands[band]['max-op-fr'],
                # "weather": random.choice(self.weather_types),
                # "density": random.choice(self.density_types),
                "location": random.choice(self.locations),
                "data_type": random.choice(self.traffic_types),
                "start_time": time,
                "duration": duration
            })

    def store_environment_data_to_file(self):
        output = pandas.DataFrame(self.environment)
        output.to_csv("out/context_database.csv", index=False)

        self.environment = []

    def yield_environment(self):
        if not self.environment:
            return None

        for item in self.environment:
            yield item

    def return_environment(self):
        return self.environment
