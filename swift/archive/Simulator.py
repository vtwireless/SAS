import random


class Simulator:
    # Config keys
    PARTIAL_BAND_SUPPORT = False

    PU_Types = ['DBS', 'MVDDS', 'NGSOFSS']

    def get_location_data(self):
        weather = self.get_fading_levels()
        locations = self.get_locations()
        data = []

        for i in range(len(locations)):
            data.append({
                'location': locations[i],
                'fading': random.choice(weather),
                'number_of_su': random.randint(20, 100)
            })

        return data

    @staticmethod
    def get_locations():
        return [f"loc{i + 1}" for i in range(30)]

    @staticmethod
    def get_fading_levels():
        return ['low', 'average', 'high', 'severe']

    def get_user_data(self):
        mobile = [True, False]
        user_type = self.get_user_classes()
        locations = self.get_locations()
        data = []

        for i in range(500):
            user_class = random.choice(user_type)
            current_band, op_bands = self.get_operating_bands(user_class)
            data.append({
                'id': str(i + 1),
                'location': random.choice(locations),
                'mobile': random.choice(mobile),
                'class': user_class,
                'op_freq': current_band,
                'allowed_bands': op_bands
            })

        return data

    @staticmethod
    def get_user_classes():
        return ['ordinary', 'emergency', 'scientific', 'government']

    def get_operating_bands(self, user_class):
        all_bands, number_of_bands = [(key, value) for key, value in self.get_bands().items()], 0

        if user_class in ['ordinary', 'scientific']:
            number_of_bands = random.randint(1, 2)
        elif user_class in ['government', 'emergency']:
            number_of_bands = random.randint(2, 5)

        sampled_list = random.sample(all_bands, number_of_bands)

        current_band = random.choice(sampled_list)[1]
        op_freq = random.randint(current_band[0], current_band[1])
        op_bands = [item[1] for item in sampled_list]

        return op_freq, op_bands

    @staticmethod
    def get_bands():
        return {
            "n1": [1920, 1980],
            "n2": [1850, 1910],
            "n3": [1710, 1785],
            "n5": [824, 849],
            "n7": [2500, 2570],
            "n30": [2305, 2315],
            "n34": [2010, 2025],
            "n38": [2570, 2620],
            "n40": [2300, 2400],
            "n41": [2496, 2690],
            "n48": [3550, 3700],
            "n78": [3300, 3800],
            "n79": [4400, 5000]
        }

    @staticmethod
    def get_class_priorities():
        return {
            'ordinary': 1,
            'scientific': 2,
            'government': 3,
            'emergency': 4
        }

    @staticmethod
    def get_fading_priority():
        return {
            'low': 1,
            'average': 2,
            'high': 3,
            'severe': 4
        }


