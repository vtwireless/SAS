from src import policies
from src.policies import RULE


class PriorityEngine:
    def __init__(self):
        pass

    @staticmethod
    def load_rule(band) -> policies.RULE:
        rule: RULE = policies.BANDS[band]['rule']

        if rule:
            return policies.RULES[rule]
        else:
            return policies.RULES['default']

    @staticmethod
    def calculate_score(row, rule: RULE):
        score = 0

        score += rule.user.index(row["type"]) + 1
        score += rule.weather.index(row["weather"]) + 1
        score += rule.density.index(row["density"]) + 1
        score += rule.traffic.index(row["traffic"]) + 1

        return score
