import json
import os
import pandas as pd
from DataGenerator import DataGenerator

pd.set_option("display.max_rows", None, "display.max_columns", None, 'display.max_colwidth', None)

"""
##### Now that we have the relevant context, lets decide on priorities for SUs in their individual locations:
def priority_engine():
    target_bands = [(12.2, 12.7), .... , ()]
    for location in locations:
        users = get_users_in_current_location()

        # Relevant for all SUs in a region or diff SUs may have diff scores based on their LOCATION in a REGION
        user_distribution_priority = get_SU_distribution_priority()
        pu_distribution_priority = get_PU_distribution_priority()



        for user in users:
            # Check user constraints
            if user.op_band not in target_bands:
                # Calculate priority based on which we might need to move the user into the target band
            else:
                # Ignore the user

            # Goal is to generate a score
            class_priority_score = get_class_priority(user['class'])
            location_priority_score = get_location_priority(user['location'])
            mobility_priority_score = get_mobility_priority(user['mobile'])
            traffic_priority_score = get_traffic_priority(user['traffic_type'])

            score = sum([all_priorities])

To consider:
* Divide overall space into multiple regions and every region into multiple locations.
    * Every region may have its own SU/PU distribution, available spectrum, policies, etc.
    * Operational context may vary from one location to another.
* Simulate channel characteristics - number & distribution of SU/PU, fading, path loss, etc.
"""


# Get score based on user's class/hierarchy
def get_class_priority(user_class):
    priorities = dataGen.get_class_priorities()

    return priorities.get(user_class, 0)


# Get score based on user's location. Score may be affected by multiple factors
def get_location_priority(user_location: str):
    # fading based priority
    fading_level = location_data.loc[location_data['location'] == user_location, 'fading'].item()
    priorities_based_on_fading = dataGen.get_fading_priority()
    # Other criterias are also possible

    return sum([
        priorities_based_on_fading.get(fading_level, 0)
    ])


# Get all users in a particular location
def get_users_in_location(location):
    users = user_data.loc[user_data['location'] == location, 'id']

    return list(users)


# Check if user's operational constraints are satisfied
def operating_freq_constraint(target_band, user_id):
    allowed_bands = user_data.loc[user_data['id'] == user_id, 'allowed_bands'].values[0]

    for band in list(allowed_bands):
        min_freq = band[0]
        max_freq = band[1]

        if min_freq <= target_band[0] and max_freq >= target_band[1]:
            return True, {}

    return False, {
        'target_band': target_band,
        'allowed': allowed_bands
    }


def use_rule_based_algorithm(locations, target_bands):
    priority_dict = dict()
    invalid_dict = dict()

    for location in locations:
        priority_dict[location] = None
        users = get_users_in_location(location)

        location_dict = {}
        for target_band in target_bands:
            band_key = str(target_band[0]) + "-" + str(target_band[1])
            band_data = {}
            for user in users:
                class_score, location_score, constraint_score = 0, 0, 0.0

                # Check user constraints
                constraint_flag, data = operating_freq_constraint(target_band, user)
                if not constraint_flag:
                    if user not in invalid_dict:
                        data['loc'] = location
                        invalid_dict[user] = data
                    constraint_score = float('-inf')

                # class based rank
                class_score = get_class_priority(user_data.loc[user_data['id'] == user, 'class'].item())

                # location based rank
                location_score = get_location_priority(location)

                total_score = sum([class_score, constraint_score, location_score])

                if total_score > 0:
                    band_data[user] = total_score

            location_dict[band_key] = band_data

        priority_dict[location] = location_dict

    return priority_dict, invalid_dict


def priority_engine(algorithm, target_bands: list):
    locations_under_consideration = dataGen.get_locations()
    priorities = None
    
    if algorithm == 'RULE_BASED':
        priorities = use_rule_based_algorithm(locations_under_consideration, target_bands)
    elif algorithm == 'MACHINE_BASED':
        priorities = None

    return priorities


# test
priority_file = 'out/priorities.json'
rejected_file = 'out/invalid_cases.json'

try:
    os.remove(priority_file)
    os.remove(rejected_file)
except Exception as e:
    print(str(e))

dataGen = DataGenerator()
ALGORITHM = 'RULE_BASED'
target_bands = [[2500, 2570], [2300, 2350]]

# Import data files
location_data = pd.DataFrame(dataGen.get_location_data())
location_data.head(5)

user_data = pd.DataFrame(dataGen.get_user_data())
user_data.head(5)

calculated_priorities, invalid_cases = priority_engine(ALGORITHM, target_bands)

with open(priority_file, 'w+') as outfile:
    json.dump(calculated_priorities, outfile, indent=4)
    print(f"'{priority_file}' created")

with open(rejected_file, 'w+') as outf:
    json.dump(invalid_cases, outf, indent=4)
    print(f"'{rejected_file}' created")
