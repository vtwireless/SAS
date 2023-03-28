import pandas as pd
import numpy as np

# Drivers - Will connect to external systems and collect context data
# Database - Save information as required
# Engine - Process & collate all data. Will have consist of different algorithms.


class Drivers:
    @staticmethod
    def location_driver():
        return pd.read_csv('location_data.csv')

    @staticmethod
    def user_driver():
        # return pd.read_csv('user_data.csv')
        pd.read_
        return pd.read_json('user_data.json')


class SwiftAlgorithms:
    class HeuristicApproach:
        @staticmethod
        def rules():
            pass

        def heuristic_approach(self):
            pass

    class MachineApproach:
        def machine_approach(self):
            pass


def main():
    pass


if __name__ == '__main__':
    drivers = Drivers()
    loc_df, user_df = drivers.location_driver(), drivers.user_driver()

    print()

