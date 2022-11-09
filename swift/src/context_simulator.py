import random
import pandas
from src import policies


class ContextSimulator:
    user_types, weather_types, density_types, traffic_types, bands = None, None, None, None, None

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
        time = 0
        all_bands = [band for band in self.bands]
        for i in range(self.number_of_users):
            band = random.choice(all_bands)
            duration = random.randint(60, 240)

            if time == 0:
                time += 1
            else:
                time = time + random.randint(60, duration)

            self.environment.append({
                "cbsd_id": i + 1,
                "type": random.choice(self.user_types),
                "band": band,
                # "freq_min": self.bands[band]['min-op-fr'],
                # "freq_max": self.bands[band]['max-op-fr'],
                "weather": random.choice(self.weather_types),
                "density": random.choice(self.density_types),
                "traffic": random.choice(self.traffic_types),
                # "start_time": time,
                # "duration": random.randint(60, 240)
            })

    def store_environment_data_to_file(self):
        output = pandas.DataFrame(self.environment)
        output.to_csv("out/experiment_input.csv", index=False)

        self.environment = []

    def yield_environment(self):
        if not self.environment:
            return None

        for item in self.environment:
            yield item

    def return_environment(self):
        return self.environment
