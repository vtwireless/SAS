from src.core import Core
from src.context_simulator import ContextSimulator


def main():
    simulation_mode = True
    core = Core()

    print("\n# Configuring Internal Simulator...")
    simulator_output_location, number_of_users = "out/sample_input.csv", 2000
    simulator = ContextSimulator(simulator_output_location, number_of_users)

    print("\n# Configuring SWIFT ASCENT Core according to your specifications...")
    core.set_algorithm("RULE_BASED")
    core.set_simulation_mode(simulation_mode)
    core.set_target_bands([[2500, 2570], [2300, 2350]])

    print("\n# Running Simulator and Obtaining Context Information...")
    simulator.create_environment()
    context_information = simulator.return_environment()
    simulator.store_environment_data_to_file()

    print("\n# Feeding Context Information to SA Core...")
    core.set_context(context_information)

    print("\n# Calculating Priority Scores...")
    core.run()

    print("\n# Saving Scores...")
    core.generate_results()


if __name__ == '__main__':
    main()
