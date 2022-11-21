"""
@author: Saurav Kumar [sauravk3@vt.edu]
@copyright: Wireless@VT
"""
import os
import traceback
import pandas

from src import policies
from src.priority_engine import PriorityEngine


class Core:
    priority_file_name = 'out/experiment_results.csv'
    rejected_file_name = 'out/experiment_input.csv'

    simulation_mode: bool = False
    context: any = None
    algorithm: str = "RULE_BASED"
    target_bands: [[]] = [[]]

    calculated_priorities, invalid_cases = None, None

    def __init__(self):
        self.__clear_memory()
        self.priority_engine = PriorityEngine()

    def __clear_memory(self):
        try:
            print("Removing existing files")
            os.remove(self.priority_file_name)
            os.remove(self.rejected_file_name)

        except Exception:
            print(traceback.format_exc())

    def set_algorithm(self, algorithm: str):
        if algorithm not in ["RULE_BASED", "MACHINE_BASED"]:
            raise Exception(
                "Incorrect SWIFT Ascent Algorithm setting. Please recheck"
            )

        self.algorithm = algorithm

    def get_algorithm(self):
        return self.algorithm

    def set_simulation_mode(self, mode: bool):
        self.simulation_mode = mode

        if mode:
            if self.calculated_priorities or self.invalid_cases:
                raise Exception("Clear Existing data first")

            self.initiate_simulation()

    def get_simulation_mode(self):
        return self.simulation_mode

    def initiate_simulation(self):
        """
        Core would be oblivious to where the context data comes from. It has no business knowing it.
        Context providers and brokers ensure that Core receives as much data as it needs and in the form
        that it requires.
        In case we connect the Core to a Simulator (in-built or external), the Core would
        need to define an interface for collecting data and the Simulator will have to make sure that it
        sends correct data

        Implementation:
        > Core has hooks who can consume specific data. Different contexts get different hooks.
        > A Simulator injects data into these hooks
        > Core collects, processes and stores the data. When scripts are migrated to RESTful services,
        these tasks would be done using DBs.
        > Using stored information, src generates priority.
        > This data is stored in JSON format for further use.
        """
        pass

    def get_target_bands(self):
        return self.target_bands

    def set_target_bands(self, bands: [[]]):
        self.target_bands = bands

    def get_context(self):
        return self.context

    def set_context(self, context: list):
        if not context or len(context) < 1:
            return

        # Verify if context is correct or not.
        # TODO

        # Populate context
        self.context = pandas.DataFrame(context)

    def run(self):
        """
        Perform Core activity. Currently, only supposed to generate priorities.
        > Using context, generates priority scores
        > forwards this score
        """
        for index, row in self.context.iterrows():
            band = row['band']
            rule: policies.RULE = self.priority_engine.load_rule(band)

            row['min_freq'] = policies.BANDS[band]["min-op-fr"]
            row['max_freq'] = policies.BANDS[band]["max-op-fr"]
            row["score"] = self.priority_engine.calculate_score(row, rule)

            self.context.at[index, 'min_freq'] = row['min_freq']
            self.context.at[index, 'max_freq'] = row['max_freq']
            self.context.at[index, 'score'] = row["score"]

    def generate_results(self):
        self.context = self.context.sort_values(by=['band'])
        self.context.to_csv("out/experiment_results.csv", index=False)
        print("Results Available at: out/experiment_results.csv")


class _Context:
    def __init__(
        self, cbsdId, type, band, weather, density, traffic
    ):
        self.cbsdId = cbsdId
        self.type = type
        self.band = band
        self.weather = weather
        self.density = density
        self.traffic = traffic
