from monolibro.model import Model


class Payload(Model):
    version: int = None
    sessionID: str = None
    details: dict = None
    operation: str = None
    data: dict = None
