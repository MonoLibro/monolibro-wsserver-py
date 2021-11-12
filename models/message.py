class Message:
    def __init__(self, object):
        required_fields = ["version", "sessionID", "details", "operation", "data"]
        for i in required_fields:
            setattr(self, i, object[i])