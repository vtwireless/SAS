import random
import policies
import pandas


class DataGenerator:
    user_types, weather_types, density_types, traffic_types, bands = None, None, None, None, None

    def __init__(self, outfile, number_of_users):
        self.outfile = outfile
        self.output = []

        # Experiment
        self.number_of_users = number_of_users
        self.get_constants()

    def get_constants(self):
        self.user_types = policies.USER_TYPE
        self.weather_types = policies.WEATHER
        self.density_types = policies.DENSITY
        self.traffic_types = policies.TRAFFIC
        self.bands = policies.BANDS

    def generate_data(self):
        time = 0
        all_bands = [band for band in self.bands]
        for i in range(self.number_of_users):
            band = random.choice(all_bands)
            duration = random.randint(60, 240)

            if time == 0:
                time += 1
            else:
                time = time + random.randint(60, duration)

            self.output.append({
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

        self.generate_data_file()

    def generate_data_file(self):
        output = pandas.DataFrame(self.output)
        output.to_csv("out/experiment_input.csv", index=False)


class SWIFT:
    def __init__(self, infile, outfile, number_of_users):
        self.data_generator = DataGenerator(infile, number_of_users)
        # self.data_generator.generate_data_file()

        self.infile = infile
        self.outfile = outfile
        self.dataframe = self.load_input()

        # Add Result columns
        self.dataframe['min_freq'] = 0
        self.dataframe['max_freq'] = 0
        self.dataframe['score'] = 0

        # Run the engine
        self.run()

    def load_input(self):
        dataframe = pandas.read_csv(self.infile)
        return dataframe

    def run(self):
        for index, row in self.dataframe.iterrows():
            band = row['band']
            rule: policies.RULE = self.load_rule(band)

            row['min_freq'] = policies.BANDS[band]["min-op-fr"]
            row['max_freq'] = policies.BANDS[band]["max-op-fr"]
            row["score"] = self.calculate_score(row, rule)

            self.dataframe.at[index, 'min_freq'] = policies.BANDS[band]["min-op-fr"]
            self.dataframe.at[index, 'max_freq'] = policies.BANDS[band]["max-op-fr"]
            self.dataframe.at[index, 'score'] = self.calculate_score(row, rule)

    @staticmethod
    def calculate_score(row, rule):
        score = 0

        score += rule.user.index(row["type"]) + 1
        score += rule.weather.index(row["weather"]) + 1
        score += rule.density.index(row["density"]) + 1
        score += rule.traffic.index(row["traffic"]) + 1

        return score

    def load_rule(self, band) -> policies.RULE:
        rule = self.data_generator.bands[band]['rule']

        if rule:
            return policies.RULES[rule]
        else:
            return policies.RULES['default']

    def generate_results(self):
        self.dataframe = self.dataframe.sort_values(by=['band'])
        self.dataframe.to_csv(self.outfile, index=False)


def main():
    infile = "out/sample_input.csv"
    outfile = "out/experiment_results.csv"

    number_of_users = 10000
    swift = SWIFT(infile, outfile, number_of_users)
    swift.generate_results()


if __name__ == '__main__':
    main()
