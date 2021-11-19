import json

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey

from monolibro.models import Payload
from utils import base64


def encode(payload: Payload, private_key: RSAPrivateKey):
    payload_encoded = base64.encode_url_no_padding(payload.json().encode())
    signature = private_key.sign(
        payload_encoded.encode(),
        padding.PSS(
            padding.MGF1(hashes.SHA256()),
            padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    signature_encoded = base64.encode_url_no_padding(signature)

    return f"{payload_encoded}.{signature_encoded}"


class MalformedMessageError(Exception):
    pass


def decode(raw_msg: str, public_key: RSAPublicKey) -> (Payload, bytes):
    raw_msg_slices = raw_msg.split(".")
    if len(raw_msg_slices) != 2:
        raise MalformedMessageError("more than one message parts are found")

    payload_encoded = raw_msg_slices[0]
    signature_encoded = raw_msg_slices[1]

    signature = base64.decode_url_no_padding(signature_encoded)
    public_key.verify(
        signature, payload_encoded.encode(),
        padding.PSS(
            padding.MGF1(hashes.SHA256()),
            padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    payload = Payload(**json.loads(base64.decode_url_no_padding(payload_encoded)))

    return payload, signature
