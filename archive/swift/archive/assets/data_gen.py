import json
import random
import os


def get_locations():
    return ['loc1', 'loc2', 'loc3', 'loc4', 'loc5', 'loc6', 'loc7', 'loc8', 'loc9', 'loc10', 'loc11', 'loc12', 'loc13',
            'loc14', 'loc15', 'loc16', 'loc17', 'loc18', 'loc19', 'loc20', 'loc21', 'loc22', 'loc23', 'loc24', 'loc25',
            'loc26', 'loc27', 'loc28', 'loc29', 'loc30']


def get_bands():
    return {
        "L": [1, 2], "S": [2, 4], "C": [4, 8], "X": [8, 12], "KU": [12, 18],
        "K": [18, 26.5], "KA": [26.5, 40], "Q": [32, 50], "U": [40, 60],
        "V": [50, 75], "W": [75, 100]
    }


def get_operating_bands():
    all_bands = [(key, value) for key, value in get_bands().items()]
    number_of_bands = random.randint(1, 3)
    # max_index = len(all_bands) - 1 - number_of_bands
    # starting_index = random.randint(0, max_index)
    #
    # sample_list = all_bands[starting_index: starting_index + number_of_bands]
    sampled_list = random.sample(all_bands, number_of_bands)
    # print(f"number: {number_of_bands}, sampled: {len(sampled_list)}")

    return [item[1] for item in sampled_list]


def write_to_file(data, filename):
    try:
        os.remove(filename)
    except Exception as e:
        print(str(e))

    with open(filename, 'w+') as file:
        for line in data:
            file.write(','.join(line) + '\n')


def user_data():
    # User data
    # number of bands a user can support,
    columns = ['user_id', 'location', 'mobile', 'user_type', 'freq_min', 'freq_max']
    mobile = ['yes', 'no']
    user_type = ['ordinary', 'public_safety', 'scientific', 'government']
    # filename = 'user_data.csv'
    locations = get_locations()
    data = {"data": []}

    for i in range(100):
        entry = {"id": str(i + 1), 'location': random.choice(locations), 'mobile': random.choice(mobile),
                 'class': random.choice(user_type), 'op_freqs': get_operating_bands()}
        data['data'].append(entry)

    with open('user_data.json', 'w+') as file:
        json.dump(data, file, indent=4, sort_keys=True)

    # data = [columns]
    # for i in range(200):
    #     freq_min = random.randint(300, 1200) / 100
    #     data.append([
    #         str(i + 1), random.choice(locations), random.choice(mobile),
    #         random.choice(user_type), str(freq_min), "{:.2f}".format(freq_min + random.randint(50, 200) / 100)
    #     ])
    #
    # write_to_file(data, filename)


def location_data():
    # User data
    # columns = ['location', 'fading', 'number_of_su', 'channel_occupancy']
    columns = ['location', 'fading', 'number_of_su']
    weather = ['low', 'average', 'high', 'severe']
    filename = 'location_data.csv'
    locations = get_locations()
    data = [columns]

    for i in range(len(locations)):
        data.append([
            locations[i], random.choice(weather),
            str(random.randint(20, 100)),
            # str(random.randint(100, 7000)/100)
        ])

    write_to_file(data, filename)


if __name__ == '__main__':
    user_data()
    location_data()
