import os
from typing import Optional
import requests
from flask import current_app
from dotenv import load_dotenv
from pydantic import BaseModel

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
                url=current_app.config["KV_URL"],
                rest_api_url=current_app.config["KV_REST_API_URL"],
                rest_api_token=current_app.config["KV_REST_API_TOKEN"],
                rest_api_read_only_token=current_app.config["KV_REST_API_READ_ONLY_TOKEN"],
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

    def set(self, key: str, value: str, opts: Optional[Opts] = None) -> bool:
        headers = {
            'Authorization': f'Bearer {self.kv_config.rest_api_token}',
        }

        url = f'{self.kv_config.rest_api_url}/set/{key}/{value}'

        if opts:
            params = opts.dict(exclude_none=True)
            for k, v in params.items():
                url += f'/{k}/{v}'

        resp = requests.post(url, headers=headers)
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