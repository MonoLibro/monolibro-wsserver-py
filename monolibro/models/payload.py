class Payload:
    version: int = None
    sessionID: str = None
    details: dict = None
    operation: str = None
    data: dict = None

    def __init__(self, obj):
        required_attrs = ["version", "sessionID", "details", "operation", "data"]
        for attr in required_attrs:
            setattr(self, attr, obj[attr])
