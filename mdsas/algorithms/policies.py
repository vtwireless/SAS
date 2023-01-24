class RULE:
    channel_size = 10
    user = ['ordinary', 'scientific', 'educational', 'government', 'emergency']
    weather = ['clear', 'cloudy', 'overcast', 'rain', 'snow', 'emergency']
    density = ['rural', 'semi-urban', 'urban']
    traffic = ['other', 'audio', 'video', 'data', 'emergency']

    def asDict(self):
        return {
            "channel_size": self.channel_size,
            "user": self.user,
            "weather": self.weather,
            "density": self.density,
            "traffic": self.traffic
        }


# In[CONSTANTS]
PU_TYPE = ['DBS', 'MVDDS', 'NGSOFSS']
USER_TYPE = ['ordinary', 'scientific', 'educational', 'government', 'emergency']
WEATHER = ['clear', 'overcast', 'cloudy', 'rain', 'snow', 'emergency']
DENSITY = ['rural', 'semi-urban', 'urban']
TRAFFIC = ['video', 'data', 'voice', 'emergency']


# In[RULES]
RULES = {
    "default": RULE(),
    "NEW_RULE": RULE(),
    "Another_Rule": RULE()
}

RULES["NEW_RULE"].density = RULES["default"].density[::-1]
RULES["NEW_RULE"].weather = RULES["default"].weather[::-1]
RULES["NEW_RULE"].channel_size = 20

RULES["Another_Rule"].traffic = RULES["default"].traffic[::-1]
RULES["Another_Rule"].user = RULES["default"].user[::-1]


# In[BANDS]
BANDS = {
    "n1": {
        "min-op-fr": 3400, "max-op-fr": 3500,
        "rule": "NEW_RULE"
    },
    "n2": {
        "min-op-fr": 3500, "max-op-fr": 3600,
        "rule": None
    },
    "n3": {
        "min-op-fr": 3600, "max-op-fr": 3700,
        "rule": None
    },
    "n4": {
        "min-op-fr": 3700, "max-op-fr": 3800,
        "rule": None
    },
    "n5": {
        "min-op-fr": 3800, "max-op-fr": 3900,
        "rule": "NEW_RULE"
    },
}
