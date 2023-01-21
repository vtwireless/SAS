import json
import os
import glob

import pytest
print(os.getcwd())
from rest_server import socket as flask_app
import re


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """data from the output of pytest gets processed here
     and are passed to pytest_html_results_table_row"""
    outcome = yield
    report = outcome.get_result()

    testcase = str(item.function.__doc__)
    c = str(item.function.__name__)[5:]

    report.testcase = f"{c} [{testcase}]"
    report.tag = re.split(r"\[|\]", report.nodeid)[0]

    # print(report.skipped)
    if report.skipped:
        message = report.longrepr[-1].split('Skipped: ')[-1]
        report.longrepr = (message, '', '')


@pytest.fixture
def app():
    yield flask_app


@pytest.fixture
def data():
    try:
        with open("./tests/data_assets/test_data.json", "r+") as infile:
            return json.load(infile)
    except FileNotFoundError as err:
        with open("./data_assets/test_data.json", "r+") as infile:
            return json.load(infile)


@pytest.fixture
def client(app):
    return app.test_client()


def pytest_sessionfinish(session, exitstatus):
    """Cleanup archive directory once we are finished."""
    files = glob.glob('tests/reports/archive/*.json')

    for f in files:
        os.remove(f)


def check_standard_failure(message, response, status=0):
    assert "status" in response
    assert "message" in response

    assert response["status"] == status
    assert response["message"] == message


def check_standard_success(message, response, status=1):
    check_standard_failure(message, response, status)


def check_winnforum_success(body):
    assert "response" in body
    assert "responseCode" in body["response"]
    assert "responseMessage" in body["response"]
    assert body["response"]["responseCode"] == '0'
    assert body["response"]["responseMessage"] == 'SUCCESS'


def not_implemented():
    return "NOT IMPLEMENTED"


def fix_needed():
    return "TODO: Fix Needed in Code"
