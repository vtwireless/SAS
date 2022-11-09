from src.core import Core
from src.context_simulator import ContextSimulator


def main():
    simulation_mode = True
    core = Core()

    print("\n# Configure the Simulator")
    simulator_output_location, number_of_users = "out/sample_input.csv", 10000
    simulator = ContextSimulator(simulator_output_location, number_of_users)

    print("\n# Configure the SWIFT ASCENT Core to your specification")
    core.set_algorithm("RULE_BASED")
    core.set_simulation_mode(simulation_mode)
    core.set_target_bands([[2500, 2570], [2300, 2350]])

    print("\n# Run Simulator and Obtain Context Information")
    simulator.create_environment()
    context_information = simulator.return_environment()
    simulator.store_environment_data_to_file()

    print("\n# Feed Context Information to src")
    core.set_context(context_information)

    print("\nRun Code")
    core.run()

    print("\n# Generate results for reading")
    core.generate_results()


if __name__ == '__main__':
    main()
