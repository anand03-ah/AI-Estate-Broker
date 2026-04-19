class Hindsight:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.logs = []

    def log(self, message):
        self.logs.append(message)
        return {
            "status": "logged",
            "message": message,
            "total_logs": len(self.logs)
        }

    def get_logs(self):
        return self.logs