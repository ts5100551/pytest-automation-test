import os
import json
import yaml
from urllib.parse import urljoin

from api.base_api import BaseAPI
from common.common import decrypt_key, get_datetime


class Test2API(BaseAPI):

    def __init__(self) -> None:
        super().__init__()
        self.base_url = self.get_url()
        self.pwd = os.getenv("pwd")

    def get_config(self) -> dict:
        """讀取 configuration 檔案取得 config 資料

        Returns:
            dict: configuration 中 Test2 的資料
        """
        config_path = os.path.join("configurations", "config.yaml")
        with open(config_path) as f:
            d = yaml.load(f.read(), Loader=yaml.SafeLoader)
        return d["Test2API"]

    def get_api_key(self) -> str:
        """解密 Test2 的 API Key

        Returns:
            str: Test2 API Key
        """
        config = self.get_config()
        return decrypt_key(config["key"], pwd=self.pwd)

    def get_url(self) -> str:
        """取得 Test2 的 host url

        Returns:
            str: Test2 host url
        """
        config = self.get_config()
        return config["host"]

    def gen_key_string(self) -> str:
        """根據當下時間動態產生 license key string

        Returns:
            str: license key string
        """
        return f'Test-{get_datetime(type="datetime_s")}'

    def get_user_ids(self, username: str) -> dict:
        """取得 config 中特定的 user_id 與 device_id 資訊

        Args:
            username (str): 指定的 user

        Returns:
            dict: user_id 與 device_id 的 dict
        """
        config = self.get_config()
        user = config["user"].get(username, None)
        if not user:
            return None
        return {
            "user_id": user.get("user_id", None),
            "device_id": user.get("device_id", None),
        }

    def action_import(self, data: list) -> object:
        """將 list 中每一個資料都做 Test2 /v1/import API

        Args:
            data (list): import key 所需的資料組成的 list

        Returns:
            object: requests 的 response object
        """
        api_key = self.get_api_key()
        payload = json.dumps(
            [
                {"key": d[0], "test_name": d[1], "test_info": d[2], "test_number": d[3]}
                for d in data
            ]
        )
        res, duration = self.send(
            api_key=api_key, method="POST", url="/v1/import", payload=payload
        )
        return res

    def action_key(self, data: list) -> object:
        """將 list 中每一把 key 都做 Test2 /v1/key API

        Args:
            key (list): key string list

        Returns:
            object: requests 的 response object
        """
        api_key = self.get_api_key()
        payload = json.dumps([key for key in data])
        res, duration = self.send(
            api_key=api_key, method="POST", url="/v1/key", payload=payload
        )
        return res

    def action_activate(self, data: list) -> object:
        """將 list 中每一個資料都做 Test2 /v1/activate API

        Args:
            data (list): (key, user_id) 組成的 list

        Returns:
            object: requests 的 response object
        """
        api_key = self.get_api_key()
        payload = json.dumps([{"key": d[0], "user_id": d[1]} for d in data])
        res, duration = self.send(
            api_key=api_key, method="POST", url="/v1/activate", payload=payload
        )
        return res

    def action_deactivate(self, key: str, user_id: str) -> object:
        """將帶入的 key, user_id 做 Test2 /v1/deactivate API

        Args:
            key (str): license key string
            user_id (str): user_id

        Returns:
            object: requests 的 response object
        """
        api_key = self.get_api_key()
        payload = json.dumps({"key": key, "user_id": user_id})
        res, duration = self.send(
            api_key=api_key, method="POST", url="/v1/deactivate", payload=payload
        )
        return res

    def action_link_device(self, data: list) -> object:
        """將 list 中每一個資料都做 Test2 /v2/link_device API

        Args:
            data (list): (key, user_id) 組成的 list

        Returns:
            object: requests 的 response object
        """
        api_key = self.get_api_key()
        payload = json.dumps(
            [{"key": d[0], "user_id": d[1], "device_id": d[2]} for d in data]
        )
        res, duration = self.send(
            api_key=api_key, method="POST", url="/v2/link_device", payload=payload
        )
        return res

    def action_unlink(self, key: str, user_id: str, device_id: str) -> object:
        """將帶入的 key, user_id, device_id 做 Test2 /v1/unlink_device API

        Args:
            key (str): license key string
            user_id (str): user_id
            device_id (str): device_id

        Returns:
            object: requests 的 response object
        """
        api_key = self.get_api_key()
        payload = json.dumps({"key": key, "user_id": user_id, "device_id": device_id})
        res, duration = self.send(
            api_key=api_key, method="POST", url="/v1/unlink_device", payload=payload
        )
        return res

    def action_lock(self, key: str, locked: bool) -> object:
        """將指定的 license key 做 lock/unlock 操作

        Args:
            key (str): license key string
            action (bool): lock True/False

        Returns:
            object: requests 的 response object
        """
        api_key = self.get_api_key()
        payload = json.dumps({"key": key, "locked": locked})
        res, duration = self.send(
            api_key=api_key, method="POST", url="/v1/lock", payload=payload
        )
        return res

    def send(self, api_key: str, method: str, url: str, payload: str) -> object:
        """根據帶入的參數做 API request

        Args:
            api_key (str): Test2 API Key
            method (str): HTTP method
            url (str): API url
            payload (str): API payload

        Returns:
            object: requests 的 response object
        """

        headers = {"Content-Type": "application/json", "X-API-KEY": api_key}
        payload = json.loads(payload)
        url = urljoin(self.base_url, url)

        if method == "GET":
            return self._send_request(
                method="GET", url=url, headers=headers, params=payload
            )

        elif method == "POST":
            return self._send_request(
                method="POST", url=url, headers=headers, json=payload
            )
