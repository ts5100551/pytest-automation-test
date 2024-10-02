import os
import json
import requests
from typing import Tuple
from jsonschema import validate
from jsonschema.exceptions import SchemaError, ValidationError

from common.convert import modify_none


# 定義 BaseAPI 類別
class BaseAPI:

    # 初始化 BaseAPI 類別，設定 requests.Session 和 timeout
    def __init__(self):
        self._session = requests.Session()
        self._timeout = 30

    # 發送 API 請求的方法，使用指定的 HTTP method 和 URL，並帶入額外的 kwargs
    def _send_request(self, method: str, url: str, **kwargs) -> Tuple[object, int]:
        try:
            # 使用 requests.Session.request() 方法發送請求並記錄請求時間
            response = self._session.request(method, url, **kwargs, timeout=self._timeout)
            duration = response.elapsed.total_seconds()
        except requests.exceptions.Timeout as e:
            # 若發生 TimeoutError 則拋出例外
            raise Exception(f"TimeoutError > {self._timeout}s")
        except requests.exceptions.RequestException as e:
            # 若發生其他 RequestException 則回傳 None 和 0，並印出錯誤訊息
            response, duration = None, 0
            print(f"Request Error > url: [{method}] {url}, kwargs: {kwargs}, error: {str(e)}")
        # 回傳 API 回應物件和 API 請求時間
        return response, duration

    def _valid_format(self, project: str, api: str, instance: dict) -> list:
        # 載入該 API 的回應資料 Format 檔案
        try:
            # 根據參數拼接出 schema 檔案的路徑並讀取 schema 檔案內容
            path = os.path.join('format', project.lower(), f'{api}.json')
            with open(file=path, mode='r', encoding='utf-8') as f:
                ori_data = f.read()
            schema = json.loads(ori_data)
        except:
            # 若讀取或轉換失敗，回傳 'FAIL' 與錯誤訊息
            msg = 'Load schema file failed.'
            return ['FAIL', msg]

        # 回應資料整理: 將部分型態定義為 integer 或是 number 的屬性 None 轉為 0, 其餘型態定義為 string 的屬性 None 轉為 "" 
        try:  
            target = modify_none(dic=instance)
        except:
            # 整理失敗，回傳 'FAIL' 與錯誤訊息
            msg = 'Modify null value failed.'
            return ['FAIL', msg]
        
        # 執行 Format 驗證
        try:
            # 使用 jsonschema 的 validate 方法進行驗證
            validate(instance=target, schema=schema)
        except SchemaError as e:
            # 驗證失敗，Schema 有錯
            msg = f'Schema error, Message：{e.message}'
            return ['FAIL', msg]
        except ValidationError as e:
            # 驗證失敗，Response 格式與 Schema 有異
            msg = f'Response JSON format not match the schema, Message：{e.message}'
            return ['FAIL', msg]
        else:
            # 驗證成功
            msg = 'Format verify passed.'
            return ['PASS', msg]