import json
import requests
from enum import Enum


class HttpMethod(Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'


class BaseSimulator:
    POST_HEADERS, GET_HEADERS = {'Content-Type': 'application/json'}, {}
    HOST, PORT = 'localhost', 8000
    ASSETS = '../data_assets/'
    payloads = None

    def __init__(self):
        with open(self.ASSETS + "test_data.json", 'r+') as infile:
            self.payloads = json.load(infile)

    def send_request_to_server(self, method: HttpMethod, url: str):
        URL = f"http://{self.HOST}:{self.PORT}/{url}"

        response = None
        if method == HttpMethod.GET:
            response = requests.request("GET", URL, headers=self.GET_HEADERS, data={})

        elif method == HttpMethod.POST:
            response = requests.request(
                "POST", URL, headers=self.POST_HEADERS, data=json.dumps(self.payloads[url])
            )

        return response.json()

    @staticmethod
    def response_handler(response):
        print("Results: ", response)

    @staticmethod
    def print_header_banner(message=None):
        if not message:
            message = "Welcome to the SAS Game. Here, you can use inputs to simulate a Spectrum Sharing Scenario"

        print(message)

    @staticmethod
    def print_footer_banner(message=None):
        if not message:
            message = "\n\nThank you for playing"

        print(message)

    @staticmethod
    def print_game_options(message=None):
        if not message:
            message = """\nYou can use the following options to perform an action:
    - GET_NODES - Fethes all nodes from the simulator
    - CREATE_NODES - Dynamically create and place N nodes
    - HELP - View this message again
"""

        print(message)

    def option_decoder(self, option, params):
        if option == 'GET_NODES':
            self.get_nodes()
        elif option == 'CREATE_NODES':
            self.add_node(params)
        else:
            self.print_game_options()

    def get_nodes(self):
        response = self.send_request_to_server(HttpMethod.GET, 'getNodesRequest')
        self.response_handler(response)

    def add_node(self, count):
        print("nodes added")
