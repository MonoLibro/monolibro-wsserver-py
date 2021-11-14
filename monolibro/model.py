class Model:
    def __init__(self, json: dict) -> None:
        for key, value in json.items():
            if hasattr(self, key):
                setattr(self, key, value)
