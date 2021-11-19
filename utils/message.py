import json

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from pydantic import ValidationError

from monolibro.models import Payload
from utils import base64


class DeserializePayloadError(Exception):
    pass


def deserialize(message: str, private_key: RSAPrivateKey) -> Payload:
    payload_encrypted = base64.decode_url_no_padding(message)

    payload_json = private_key.decrypt(
        payload_encrypted,
        padding.OAEP(
            padding.MGF1(hashes.SHA256()),
            hashes.SHA256(),
            None
        )
    )

    try:
        payload = Payload(**json.loads(payload_json))
    except ValidationError:
        raise DeserializePayloadError("missing information in payload")

    return payload
