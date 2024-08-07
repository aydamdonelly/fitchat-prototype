import os
from typing import Optional
import requests
from flask import current_app
from dotenv import load_dotenv
from pydantic import BaseModel
import json
from datetime import datetime

load_dotenv()

class KVConfig(BaseModel):
    url: str
    rest_api_url: str
    rest_api_token: str
    rest_api_read_only_token: str

class Opts(BaseModel):
    ex: Optional[int] = None
    px: Optional[int] = None
    exat: Optional[int] = None
    pxat: Optional[int] = None
    keepTtl: Optional[bool] = None

class KV:
    """
    Wrapper for https://vercel.com/docs/storage/vercel-kv/rest-api
    """

    def __init__(self, kv_config: Optional[KVConfig] = None):
        if kv_config is None:
            self.kv_config = KVConfig(
                url=os.getenv("KV_URL"),
                rest_api_url=os.getenv("KV_REST_API_URL"),
                rest_api_token=os.getenv("KV_REST_API_TOKEN"),
                rest_api_read_only_token=os.getenv("KV_REST_API_READ_ONLY_TOKEN"),
            )
        else:
            self.kv_config = kv_config

    def get_kv_conf(self) -> KVConfig:
        return self.kv_config

    def has_auth(self) -> bool:
        headers = {
            'Authorization': f'Bearer {self.kv_config.rest_api_token}',
        }
        resp = requests.get(self.kv_config.rest_api_url, headers=headers)
        if resp.status_code != 200:
            return False
        return 'error' not in resp.json()

    def set(self, key: str, value: dict, opts: Optional[Opts] = None) -> bool:
        headers = {
            'Authorization': f'Bearer {self.kv_config.rest_api_token}',
            'Content-Type': 'application/json'
        }

        url = f'{self.kv_config.rest_api_url}/set/{key}'

        if opts:
            params = opts.dict(exclude_none=True)
            for k, v in params.items():
                url += f'/{k}/{v}'

        # Convert the value to JSON string using the custom encoder
        payload = json.dumps(value, cls=CustomJSONEncoder)

        # Send the data in the body of the POST request
        resp = requests.post(url, headers=headers, data=payload)
        if resp.status_code == 200:
            return resp.json().get('result', False)
        return False

    def get(self, key: str) -> Optional[str]:
        headers = {
            'Authorization': f'Bearer {self.kv_config.rest_api_token}',
        }

        resp = requests.get(f'{self.kv_config.rest_api_url}/get/{key}', headers=headers)
        if resp.status_code == 200:
            return resp.json().get('result')
        return None

# Custom JSON encoder for datetime objects
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(CustomJSONEncoder, self).default(obj)