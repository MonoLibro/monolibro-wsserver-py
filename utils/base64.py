import base64


def encode_url_no_padding(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").split("=")[0]


def decode_url_no_padding(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + '=' * (4 - len(data) % 4))
