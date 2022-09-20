"""
REST API Server for CCI-MDSAS

Created: Sept 20, 2022
Author/s: Saurav Kumar
Advised by Dr. Carl Dietrich (cdietric@vt.edu)
For Wireless@VT
"""
import uvicorn
from fastapi import FastAPI
import threading
import time

from controllers import DatabaseController
from algorithms import SASAlgorithms
from algorithms import SASREM
from Utilities import Utilities
from settings import settings
from rest_models import *


if settings.ENVIRONMENT == 'DEVELOPMENT':
    db = DatabaseController.DatabaseController(True)
else:
    db = DatabaseController.DatabaseController(False)

REM = SASREM.SASREM()
SASAlgorithms = SASAlgorithms.SASAlgorithms()


app = FastAPI()


@app.get("/")
def root():
    return {"message": "Server is Running!"}


@app.post("/suLogin/")
def secondaryUserLogin(data: LoginModel):
    try:
        response = db.authenticate_user(data.dict(), False)
        return response

    except Exception as err:
        return {
            'status': 0, 'message': str(err)
        }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
