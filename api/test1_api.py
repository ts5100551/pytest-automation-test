import os
from urllib.parse import urljoin

import yaml

from api.base_api import BaseAPI


class Test1API(BaseAPI):

    def __init__(self):
        super().__init__()
        self.base_url = self.get_base_url()
        self.pwd = os.getenv("pwd")
        self.project = "test1_api"

    def get_base_url(self):
        config_path = os.path.join("configurations", "config.yaml")
        with open(config_path) as f:
            d = yaml.load(f.read(), Loader=yaml.SafeLoader)
            url = d["Test1API"]["host"]
        return url

    def send(
        self,
        user_id: int,
        key: str,
        api_key: str,
        method: str,
        url: str,
        payload: str,
    ):
        headers = {
            "X-API-Delegate": str(user_id),
            "X-API-Key": str(api_key),
        }

        payload = eval(payload)

        if method == "GET":
            response, duration = self._send_request(
                method="GET",
                url=urljoin(self.base_url, url),
                headers=headers,
                params=payload,
            )

        elif method == "POST":
            response, duration = self._send_request(
                method="POST",
                url=urljoin(self.base_url, url),
                headers=headers,
                json=payload,
            )

        request_id = response.headers.get("x-api-requestid")
        print(f"x-api-requestid: {request_id}")

        return response, duration

    def validate_format(self, api: str, data: dict) -> list:
        return self._valid_format(project=self.project, api=api, instance=data)
