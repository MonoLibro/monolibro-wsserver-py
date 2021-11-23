import json

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from pydantic import ValidationError

from monolibro.models import Payload
from utils import base64


class DeserializePayloadError(Exception):
    pass


def deserialize(message: str, public_key: RSAPublicKey) -> (Payload, bool):
    message_slices = message.split(".")

    payload_encoded = message_slices[0]
    signature = base64.decode_url_no_padding(message_slices[1])

    if public_key:
        try:
            public_key.verify(
                signature,
                payload_encoded.encode(),
                padding.PSS(
                    padding.MGF1(hashes.SHA256()),
                    padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            match = True
        except ValidationError:
            match = False
    else:
        match = False

    payload_bytes = base64.decode_url_no_padding(payload_encoded)

    try:
        payload = Payload(**json.loads(payload_bytes))
    except ValidationError:
        raise DeserializePayloadError("missing information in payload")

    return payload, match
