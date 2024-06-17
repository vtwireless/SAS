import glob
import json
import math
import os
import uuid
import pandas as pd

from settings import settings
from Utilities import Utilities
from algorithms import PrioritizationFramework


class SIMInput:
    @staticmethod
    def get_input(lat_FSS: float, lon_FSS: float, radius: int, simulation_count: int, bs_ue_max_radius: int,
                  bs_ue_min_radius: int, base_station_count: int, base_stations: dict, rain: bool, rain_rate: float,
                  exclusion_zone_radius: float):
        return {
            "lat_FSS": lat_FSS,
            "lon_FSS": lon_FSS,
            "radius": radius,
            "simulation_count": simulation_count,
            "bs_ue_max_radius": bs_ue_max_radius,
            "bs_ue_min_radius": bs_ue_min_radius,
            "base_station_count": base_station_count,
            "base_stations": base_stations,
            "rain": rain,
            "rain_rate": rain_rate,
            "exclusion_zone_radius": exclusion_zone_radius
        }


class ASCENTController:
    INCLUSION_ZONE_RADIUS = None
    EXCLUSION_ZONE_RADIUS = None
    EXCLUSION_ZONE_RADIUS_STEP = None
    SIMULATION_COUNT = None
    BS_COUNT = None
    BS_UE_RADIUS_MIN = None
    BS_UE_RADIUS_MAX = None
    FSS_COOR = None
    BASE_STATIONS: pd.DataFrame = None

    sim_input = SIMInput()
    settings_file = settings.SIM_SETTINGS_FILE

    def __init__(self):
        self.INCLUSION_ZONE_RADIUS = settings.INCLUSION_ZONE_RADIUS
        self.EXCLUSION_ZONE_RADIUS = settings.EXCLUSION_ZONE_RADIUS
        self.EXCLUSION_ZONE_RADIUS_STEP = settings.EXCLUSION_ZONE_RADIUS_STEP
        self.SIMULATION_COUNT = settings.SIMULATION_COUNT
        self.BS_COUNT = settings.BS_COUNT
        self.BS_UE_RADIUS_MIN = settings.BS_UE_RADIUS[0]
        self.BS_UE_RADIUS_MAX = settings.BS_UE_RADIUS[1]

        self.FSS_COOR = [37.20250, -80.43444]  # Hard-coded

        self.rain, self.rain_rate = False, 0.0

        try:
            fss_weather_info = PrioritizationFramework.get_weather(self.FSS_COOR[0], self.FSS_COOR[1])
            self.rain_rate = fss_weather_info.get("days")[0]["precip"]
            if self.rain_rate != float(0):
                self.rain = True
        except Exception as err:
            print(err)

        self.BASE_STATIONS = self.generate_BS_list(self.BS_COUNT)

        sim_settings = self.configure_simulator_settings()

        # self.implement_exclusion_zone()
        # print(json.dumps(self.BASE_STATIONS[self.BASE_STATIONS["status"] == 0].to_dict("records"), indent=4))

    def configure_simulator_settings(self, sim_sett=None):
        if sim_sett is None:
            sim_sett = {}

        self.INCLUSION_ZONE_RADIUS = sim_sett.get("radius", self.INCLUSION_ZONE_RADIUS)
        self.EXCLUSION_ZONE_RADIUS = sim_sett.get("exclusion_radius", self.EXCLUSION_ZONE_RADIUS)
        self.EXCLUSION_ZONE_RADIUS_STEP = sim_sett.get("exclusion_radius_step", self.EXCLUSION_ZONE_RADIUS_STEP)
        self.SIMULATION_COUNT = sim_sett.get("simulation_count", self.SIMULATION_COUNT)
        self.BS_UE_RADIUS_MAX = sim_sett.get("bs_ue_max_radius", self.BS_UE_RADIUS_MAX)
        self.BS_UE_RADIUS_MIN = sim_sett.get("bs_ue_min_radius", self.BS_UE_RADIUS_MIN)
        self.rain = sim_sett.get("rain", self.rain)

        if "base_station_count" in sim_sett:
            if sim_sett["base_station_count"] != self.BS_COUNT:
                self.BS_COUNT = sim_sett.get("base_station_count", self.BS_COUNT)
                self.BASE_STATIONS = self.generate_BS_list(self.BS_COUNT)

        data = {
            "radius": self.INCLUSION_ZONE_RADIUS,
            "exclusion_radius": self.EXCLUSION_ZONE_RADIUS,
            "exclusion_radius_step": self.EXCLUSION_ZONE_RADIUS_STEP,
            "simulation_count": self.SIMULATION_COUNT,
            "bs_ue_max_radius": self.BS_UE_RADIUS_MAX,
            "bs_ue_min_radius": self.BS_UE_RADIUS_MIN,
            "rain": self.rain,
            "base_station_count": self.BS_COUNT,
            "base_stations": self.BASE_STATIONS.to_dict("records")
        }

        with open(self.settings_file, "w+") as outfile:
            json.dump(data, outfile, indent=4)

        return data

    def get_simulator_input(self):
        return self.sim_input.get_input(
            self.FSS_COOR[0],
            self.FSS_COOR[1],
            self.INCLUSION_ZONE_RADIUS,
            self.SIMULATION_COUNT,
            self.BS_UE_RADIUS_MAX,
            self.BS_UE_RADIUS_MIN,
            self.BS_COUNT,
            self.BASE_STATIONS.to_dict("records"),
            self.rain,
            self.rain_rate,
            self.EXCLUSION_ZONE_RADIUS
        )

    def generate_BS_list(self, bs_count):
        path = "../data/split_excel/"
        all_files = glob.glob(os.path.join(path, "*.csv"))

        all_data = pd.concat((pd.read_csv(
            file, names=["radio", "mcc", "mnc", "lac", "cid", "unit", "longitude",
                         "latitude", "range", "samples", "changeable", "created", "updated", "averageSignal"]
        ) for file in all_files))

        latitude_range = self.INCLUSION_ZONE_RADIUS / 110574
        longitude_range = self.INCLUSION_ZONE_RADIUS / (111320 * math.cos(math.radians(latitude_range)))

        data_within_zone = all_data[
            (all_data["radio"] == "GSM")
            & (all_data["longitude"] <= (self.FSS_COOR[1] + longitude_range))
            & (all_data["longitude"] >= (self.FSS_COOR[1] - longitude_range))
            & (all_data["latitude"] <= (self.FSS_COOR[0] + latitude_range))
            & (all_data["latitude"] >= (self.FSS_COOR[0] - latitude_range))
        ].copy(deep=True)

        if len(data_within_zone) > bs_count:
            data_within_zone = data_within_zone.sample(n=bs_count)

        data_within_zone["status"] = 1
        data_within_zone["unique_id"] = [str(uuid.uuid4()) for i in range(len(data_within_zone))]
        data_within_zone["dist_from_FSS"] = [
            Utilities.calculate_distance_between_coordinates(
                data_within_zone.iloc[i]['latitude'], data_within_zone.iloc[i]['longitude'],
                self.FSS_COOR[0], self.FSS_COOR[1]
            ) for i in range(len(data_within_zone))
        ]

        return data_within_zone

    def implement_exclusion_zone(self):
        non_transmitting_bs = self.BASE_STATIONS[self.BASE_STATIONS["status"] == 0]

        while self.EXCLUSION_ZONE_RADIUS < self.INCLUSION_ZONE_RADIUS:
            # print("Attempting with Exclusion Zone Radius = ", self.EXCLUSION_ZONE_RADIUS)
            self.modify_bs_status_in_exclusion_zone()
            new_NTBS = self.BASE_STATIONS[self.BASE_STATIONS["status"] == 0]

            if len(new_NTBS) > len(non_transmitting_bs):
                # print("new exclusion zone radius = ", self.EXCLUSION_ZONE_RADIUS)
                break

            self.EXCLUSION_ZONE_RADIUS += self.EXCLUSION_ZONE_RADIUS_STEP

    def modify_bs_status_in_exclusion_zone(self):
        self.BASE_STATIONS.loc[self.BASE_STATIONS["dist_from_FSS"] <= self.EXCLUSION_ZONE_RADIUS, "status"] = 0

    def implement_simulator_feedback(self, feedback):
        feedback = {
            "Interference_values_UMi_each_Bs": [
                -31.586625574403882,
                -35.191424022093855,
                -18.56990745856593,
                -35.47686461913297,
                -38.474774043668745,
                -11.141635807315321,
                -62.20374665019345,
                -19.370609097823518,
                -26.541763404108263,
                -47.50175471126143,
                -17.88587437929757,
                -35.195019551854266,
                -52.674793302083586,
                -29.62489982828368,
                2.7971202581528343,
                6.107579300585324,
                -25.10698899447582,
                -69.47948320793697,
                -50.725313822900524,
                -55.20441399983092,
                -31.93346957378436,
                -40.95931464486423,
                -39.14056440921604,
                -21.701477074230823,
                -32.91510580409362,
                -31.42415785610693,
                -35.99502355385156,
                -26.626390561350718,
                -25.523930166508602,
                -23.923752659832083,
                -41.86998035329006,
                -47.895659185236084,
                -37.21194865204484
            ]
        }

        interference_values = feedback.get("Interference_values_UMi_each_Bs", [])
        if not interference_values:
            return {
                "status": "fail",
                "message": "no values detected under the key 'Interference_values_UMi_each_Bs'"
            }
        elif len(interference_values) != self.BS_COUNT:
            return {
                "status": "fail",
                "message": f"No. of BS is {self.BS_COUNT} while {len(interference_values)} interference values "
                           f"were provided"
            }

        if self.rain:
            threshold = settings.INR_THRESHOLD["rain"]
        else:
            threshold = settings.INR_THRESHOLD["default"]

        changed, changes = False, 0
        computed_exclusion_zone = self.EXCLUSION_ZONE_RADIUS
        for index in range(self.BS_COUNT):
            if interference_values[index] > threshold and self.BASE_STATIONS.iloc[index]['status'] != 0:
                self.BASE_STATIONS.iloc[index, self.BASE_STATIONS.columns.get_loc('status')] = 0
                changed = True
                changes += 1

                if self.BASE_STATIONS.iloc[index]["dist_from_FSS"] > computed_exclusion_zone:
                    computed_exclusion_zone = round(self.BASE_STATIONS.iloc[index].to_dict()["dist_from_FSS"], 2)

        flag = False
        for bs in self.BASE_STATIONS.sort_values('dist_from_FSS').to_dict("records"):
            distance_from_fss = bs["dist_from_FSS"]
            status = bs["status"]
            if status == 1:
                flag = True

            if distance_from_fss < computed_exclusion_zone and flag:
                computed_exclusion_zone = distance_from_fss - 1
                break

        self.EXCLUSION_ZONE_RADIUS = round(computed_exclusion_zone, 2)
        if changed:
            self.configure_simulator_settings()

        return {
            "status": "success",
            "message": f"{changes} base stations stopped from transmitting. Exclusion Zone Radius is "
                       f"{self.EXCLUSION_ZONE_RADIUS}"
        }

