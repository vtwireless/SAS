from datetime import datetime, timedelta
from math import radians, cos, sin, asin, sqrt
import random

class Simulator:
    def __init__(self, numberOfUsers, percentageMU, varianceOfData, percentageMobile, secureCount):
        self.users = []
        self.numberOfUsers = numberOfUsers
        self.varianceOfData = varianceOfData
        self.goodLow = -70
        self.goodHigh = 25
        self.PULow = 27
        self.PUHigh = 40
        self.arraySize = 16
        self.percentageMU = percentageMU
        self.percentageMobile = percentageMobile
        self.secureCount = secureCount

        #assumes this is for one frequency range

        numberMU = (numberOfUsers*percentageMU)/100
        mobile = False
        sc = 0
        for x in range(numberOfUsers):
            if self.percentageMobile < random.randrange(0, 100):
                mobile = True
            else:
                mobile = False
            if x < numberMU:#malicious node
                createUser("", True, self.percentageMU, self.generateLat(), self.generateLon, False, mobile)
            else:
                if sc < self.secureCount:#is secure
                    createUser("", False, 0, self.generateLat(), self.generateLon, True, False)
                else:#regular node
                    createUser("", False, 0, self.generateLat(), self.generateLon, False, mobile)




    def createUser(self, id, isMU, percentageMU, latitude, longitude):
        self.users.append(User("", isMU, percentageMU, latitude, longitude))


    def generateLat(self):
        lat = random.randrange(3722000,3723000)
        return (lat /100000)

    def generateLon(self):
        lon = random.randrange(8040000,8041000)
        lon = lon /100000
        return (-1 * lon)

    def makeGoodData(self):
        arr = []
        for x in range(self.arraySize):
            arr.append(self.makeData(self.goodLow, self.goodHigh))
        return arr

    def makeData(self, low, high):
        val = random.randrange(low*10000, high*10000)
        mult = random.randrange(8, 12)
        return val*(mult/10)

    def makePUData(self):
        arr = []
        for x in range(self.arraySize):
            arr.append(self.makeData(self.PULow, self.PUHigh))
        return arr


    def createPU(self):
        print("PU active")
        for user in self.users:
            if not user.isMU:
                sendData(user, self.makePUData())
            else:
                x = random.randrange(0,100)
                if x < user.percentageMU:#if user is malicious send malicious
                    sendData(user, self.makeGoodData()())
                else:
                    sendData(user, self.makePUData()())


    def normalSpectrum(self):
        print("Normal environment")
        for user in self.users:
            if not user.isMU:
                sendData(user, self.makeGoodData())
            else:
                x = random.randrange(0,100)
                if x < user.percentageMU:#if user is malicious send malicious
                    sendData(user, self.makePUData()())
                else:
                    sendData(user, self.makeGoodData()())




    def sendData(self, user, data):
        print("todo")

    def move(self):
        for user in self.users:
            if user.mobile:
                user.latitude = self.generateLat()
                user.longitude = self.generateLon()


class User:
    def __init__(self, id, isMU, percentageMU, latitude, longitude, secure, isMobile):
        self.id = id
        self.isMU = isMU
        self.percentageMU = percentageMU
        self.latitude = latitude
        self.longitude = longitude
        self.secure = secure
        self.mobile = mobile
