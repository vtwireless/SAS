class Utility:
    @staticmethod
    def response_generator(status_code, payload):
        payload['status'] = status_code
        return payload

    @staticmethod
    def success_payload(payload):
        payload["status"]: 1
        return payload

    @staticmethod
    def success_message(message):
        return {
            "status": 0,
            "message": message
        }

    @staticmethod
    def failure_message(message):
        return {
            "status": 0,
            "message": message
        }

    @staticmethod
    def already_exists(message):
        return {
            "status": 0,
            "exists": 1,
            "message": message
        }
