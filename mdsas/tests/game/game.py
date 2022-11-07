from base import BaseSimulator

simulator = BaseSimulator()
simulator.print_header_banner()
simulator.print_game_options()

while True:
    val = str(input("\nEnter TASK to perform: ")).strip().upper()
    count = None

    if val in ["ESC", "QUIT"]:
        simulator.print_footer_banner()
        break

    if val == "CREATE_NODES":
        count = int(str(input("Enter the number of nodes [Max 10 at a time]: ")).strip())

    simulator.option_decoder(val, count)


