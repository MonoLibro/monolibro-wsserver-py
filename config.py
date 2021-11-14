from pydantic import BaseModel


class Config(BaseModel):
    host: str = "127.0.0.1"
    port: int = 3200

    public_key_path: str = "./keys/pub.pem"
    private_key_path: str = "./keys/pri.key"
