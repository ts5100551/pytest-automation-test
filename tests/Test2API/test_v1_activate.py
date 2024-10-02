import json

import allure
import pytest

from api.test2_api import Test2API
from common.common import print_result
from common.load_excel import load_data, load_ids


class TestV1Activate(object):

    test2_api = Test2API()

    @pytest.mark.test
    @pytest.mark.parametrize(
        "api_id, case_id, path, description, run, method, scenario, http_response, response_code, payload",
        load_data(site="test2", api_id="activate-01"),
        ids=load_ids(site="test2", api_id="activate-01"),
    )
    def test_activate_01(
        self,
        decrypt_Test2API_key,
        is_run,
        api_id,
        case_id,
        path,
        description,
        run,
        method,
        scenario,
        http_response,
        response_code,
        payload,
    ):

        # Allure report 參數設定
        allure.dynamic.story(path)
        allure.dynamic.title(f'{api_id.replace("-", "_")}_{scenario}')
        allure.dynamic.description(description)

        # 透過 test data excel 的 is_run 欄位值決定是否要執行該 case 的測試
        if not is_run(is_run=run):
            pytest.skip()

        # 根據不同 scenario 進行測試
        # register 一把 key
        if scenario == "single":
            # 將 key 先做一次 deactivate，確保環境正確
            with allure.step("Initialization environment"):
                p = json.loads(payload)
                init_data = [[data["key"], data["user_id"]] for data in p]
                print(f"Deactivate license key for initialization environment:")
                for data in init_data:
                    init_key, init_user_id = data[0], data[1]
                    res = self.test2_api.action_deactivate(
                        key=init_key, user_id=init_user_id
                    )
                    print(f"{init_key}: {res.status_code}, {res.json()}")
                print()

            # 發送 request
            with allure.step("Send HTTP request"):
                print(f"Start testing:")
                res, duration = self.test2_api.send(
                    api_key=decrypt_Test2API_key,
                    method=method,
                    url=path,
                    payload=payload,
                )
                print_result(res)

            # 驗證 response
            with allure.step("Verify response"):
                msg = "License keys activated successfully."
                r = res.json()
                assert res.status_code == int(
                    http_response
                ), f"Error: Unexpected status code {res.status_code}, expected {http_response}."
                assert (
                    r["message"] == msg
                ), f'Error: message {r["message"]} should be "{msg}"'
                assert (
                    r["pass_count"] == 1
                ), f'Error: pass_count {r["pass_count"]} should be "1"'
                assert (
                    r["fail_count"] == 0
                ), f'Error: fail_count {r["fail_count"]} should be "0"'
                assert r["data"] == [], f'Error: data {r["data"]} should be empty list.'

            # 還原測試環境與資料
            with allure.step("Restore environment"):
                res = self.test2_api.action_deactivate(key=init_key, user_id=init_user_id)
                print(
                    f"Test done, deactivate license key for next test:\n{res.status_code}, {res.json()}"
                )

        # register 多把 key
        elif scenario == "multiple":
            # 將 key 先做一次 deactivate，確保環境正確
            with allure.step("Initialization environment"):
                p = json.loads(payload)
                init_data = [[data["key"], data["user_id"]] for data in p]
                print(f"Deactivate license key for initialization environment:")
                for data in init_data:
                    init_key, init_user_id = data[0], data[1]
                    res = self.test2_api.action_deactivate(
                        key=init_key, user_id=init_user_id
                    )
                    print(f"{init_key}: {res.status_code}, {res.json()}")
                print()

            # 發送 request
            with allure.step("Send HTTP request"):
                print(f"Start testing:")
                res, duration = self.test2_api.send(
                    api_key=decrypt_Test2API_key,
                    method=method,
                    url=path,
                    payload=payload,
                )
                print_result(res)

            # 驗證 response
            with allure.step("Verify response"):
                msg = "License keys activated successfully."
                r = res.json()
                assert res.status_code == int(
                    http_response
                ), f"Error: Unexpected status code {res.status_code}, expected {http_response}."
                assert (
                    r["message"] == msg
                ), f'Error: message {r["message"]} should be "{msg}"'
                assert (
                    r["pass_count"] == 2
                ), f'Error: pass_count {r["pass_count"]} should be "1"'
                assert (
                    r["fail_count"] == 0
                ), f'Error: fail_count {r["fail_count"]} should be "0"'
                assert r["data"] == [], f'Error: data {r["data"]} should be empty list.'

            # 還原測試環境與資料
            with allure.step("Restore environment"):
                print(f"Test done, deactivate license key for next test:")
                for data in init_data:
                    init_key, init_user_id = data[0], data[1]
                    res = self.test2_api.action_deactivate(
                        key=init_key, user_id=init_user_id
                    )
                    print(f"{init_key}: {res.status_code}, {res.json()}")

        # register 多把 key，但部分失敗
        elif scenario == "partially":
            # 將 key 先做一次 deactivate，確保環境正確
            with allure.step("Initialization environment"):
                p = json.loads(payload)
                init_data = [[data["key"], data["user_id"]] for data in p]

                init_key = init_data[1][0]
                init_user_id = init_data[1][1]
                print(f"Deactivate license key for initialization environment:")
                res = self.test2_api.action_deactivate(key=init_key, user_id=init_user_id)
                print(f"{init_key}: {res.status_code}, {res.json()}\n")

            # 發送 request
            with allure.step("Send HTTP request"):
                print(f"Start testing:")
                res, duration = self.test2_api.send(
                    api_key=decrypt_Test2API_key,
                    method=method,
                    url=path,
                    payload=payload,
                )
                print_result(res)

            # 驗證 response
            with allure.step("Verify response"):
                msg = "License keys activated partially."
                error_msg = "Cannot find License Key."
                p = json.loads(payload)
                r = res.json()
                assert res.status_code == int(
                    http_response
                ), f"Error: Unexpected status code {res.status_code}, expected {http_response}."
                assert (
                    r["message"] == msg
                ), f'Error: message {r["message"]} should be "{msg}"'
                assert (
                    r["pass_count"] == 1
                ), f'Error: pass_count {r["pass_count"]} should be "1"'
                assert (
                    r["fail_count"] == 1
                ), f'Error: fail_count {r["fail_count"]} should be "1"'
                assert (
                    r["data"] is not []
                ), f'Error: data {r["data"]} should not be empty list.'
                assert (
                    len(r["data"]) == 1
                ), f'Error: data {r["data"]} length should be "1"'
                assert (
                    r["data"][0]["key"] == p[0]["key"]
                ), f'Error: key {r["data"][0]["key"]} should be "{p[0]["key"]}"'
                assert r["data"][0]["code"] == int(
                    response_code
                ), f'Error: code {r["data"][0]["code"]} should be "{int(response_code)}"'
                assert (
                    r["data"][0]["error_msg"] == error_msg
                ), f'Error: error_message {r["data"][0]["error_msg"]} should be "{error_msg}"'

            # 還原測試環境與資料
            with allure.step("Restore environment"):
                print(f"Test done, deactivate license key for next test:")
                res = self.test2_api.action_deactivate(key=init_key, user_id=init_user_id)
                print(f"{init_key}: {res.status_code}, {res.json()}")

        # register 一把 key，但 key 已經 link to user
        elif scenario == "link_to_user":
            # 發送 request
            with allure.step("Send HTTP request"):
                print(f"Start testing:")
                res, duration = self.test2_api.send(
                    api_key=decrypt_Test2API_key,
                    method=method,
                    url=path,
                    payload=payload,
                )
                print_result(res)

            # 驗證 response
            with allure.step("Verify response"):
                msg = "License keys activated partially."
                error_msg = "License key has already activated."
                p = json.loads(payload)
                r = res.json()
                assert res.status_code == int(
                    http_response
                ), f"Error: Unexpected status code {res.status_code}, expected {http_response}."
                assert (
                    r["message"] == msg
                ), f'Error: message {r["message"]} should be "{msg}"'
                assert (
                    r["pass_count"] == 0
                ), f'Error: pass_count {r["pass_count"]} should be "0"'
                assert (
                    r["fail_count"] == 1
                ), f'Error: fail_count {r["fail_count"]} should be "1"'
                assert (
                    r["data"] is not []
                ), f'Error: data {r["data"]} should not be empty list.'
                assert (
                    len(r["data"]) == 1
                ), f'Error: data {r["data"]} length should be "1"'
                assert (
                    r["data"][0]["key"] == p[0]["key"]
                ), f'Error: key {r["data"][0]["key"]} should be "{p[0]["key"]}"'
                assert r["data"][0]["code"] == int(
                    response_code
                ), f'Error: code {r["data"][0]["code"]} should be "{int(response_code)}"'
                assert (
                    r["data"][0]["error_msg"] == error_msg
                ), f'Error: error_message {r["data"][0]["error_msg"]} should be "{error_msg}"'

        # register 一把 key，但 key 已經 link to device
        elif scenario == "link_to_device":
            # 發送 request
            with allure.step("Send HTTP request"):
                print(f"Start testing:")
                res, duration = self.test2_api.send(
                    api_key=decrypt_Test2API_key,
                    method=method,
                    url=path,
                    payload=payload,
                )
                print_result(res)

            # 驗證 response
            with allure.step("Verify response"):
                msg = "License keys activated partially."
                error_msg = "License key has already activated."
                p = json.loads(payload)
                r = res.json()
                assert res.status_code == int(
                    http_response
                ), f"Error: Unexpected status code {res.status_code}, expected {http_response}."
                assert (
                    r["message"] == msg
                ), f'Error: message {r["message"]} should be "{msg}"'
                assert (
                    r["pass_count"] == 0
                ), f'Error: pass_count {r["pass_count"]} should be "0"'
                assert (
                    r["fail_count"] == 1
                ), f'Error: fail_count {r["fail_count"]} should be "1"'
                assert (
                    r["data"] is not []
                ), f'Error: data {r["data"]} should not be empty list.'
                assert (
                    len(r["data"]) == 1
                ), f'Error: data {r["data"]} length should be "1"'
                assert (
                    r["data"][0]["key"] == p[0]["key"]
                ), f'Error: key {r["data"][0]["key"]} should be "{p[0]["key"]}"'
                assert r["data"][0]["code"] == int(
                    response_code
                ), f'Error: code {r["data"][0]["code"]} should be "{int(response_code)}"'
                assert (
                    r["data"][0]["error_msg"] == error_msg
                ), f'Error: error_message {r["data"][0]["error_msg"]} should be "{error_msg}"'

        # register 一把 key，但 key 已經 locked
        elif scenario == "locked":
            # 發送 request
            with allure.step("Send HTTP request"):
                print(f"Start testing:")
                res, duration = self.test2_api.send(
                    api_key=decrypt_Test2API_key,
                    method=method,
                    url=path,
                    payload=payload,
                )
                print_result(res)

            # 驗證 response
            with allure.step("Verify response"):
                msg = "License keys activated partially."
                error_msg = "License key has already activated."
                p = json.loads(payload)
                r = res.json()
                assert res.status_code == int(
                    http_response
                ), f"Error: Unexpected status code {res.status_code}, expected {http_response}."
                assert (
                    r["message"] == msg
                ), f'Error: message {r["message"]} should be "{msg}"'
                assert (
                    r["pass_count"] == 0
                ), f'Error: pass_count {r["pass_count"]} should be "0"'
                assert (
                    r["fail_count"] == 1
                ), f'Error: fail_count {r["fail_count"]} should be "1"'
                assert (
                    r["data"] is not []
                ), f'Error: data {r["data"]} should not be empty list.'
                assert (
                    len(r["data"]) == 1
                ), f'Error: data {r["data"]} length should be "1"'
                assert (
                    r["data"][0]["key"] == p[0]["key"]
                ), f'Error: key {r["data"][0]["key"]} should be "{p[0]["key"]}"'
                assert r["data"][0]["code"] == int(
                    response_code
                ), f'Error: code {r["data"][0]["code"]} should be "{int(response_code)}"'
                assert (
                    r["data"][0]["error_msg"] == error_msg
                ), f'Error: error_message {r["data"][0]["error_msg"]} should be "{error_msg}"'

        # register 一把 key，但 key 已經 revoked
        elif scenario == "revoked":
            # 發送 request
            with allure.step("Send HTTP request"):
                print(f"Start testing:")
                res, duration = self.test2_api.send(
                    api_key=decrypt_Test2API_key,
                    method=method,
                    url=path,
                    payload=payload,
                )
                print_result(res)

            # 驗證 response
            with allure.step("Verify response"):
                msg = "License keys activated partially."
                error_msg = "License key has already activated."
                p = json.loads(payload)
                r = res.json()
                assert res.status_code == int(
                    http_response
                ), f"Error: Unexpected status code {res.status_code}, expected {http_response}."
                assert (
                    r["message"] == msg
                ), f'Error: message {r["message"]} should be "{msg}"'
                assert (
                    r["pass_count"] == 0
                ), f'Error: pass_count {r["pass_count"]} should be "0"'
                assert (
                    r["fail_count"] == 1
                ), f'Error: fail_count {r["fail_count"]} should be "1"'
                assert (
                    r["data"] is not []
                ), f'Error: data {r["data"]} should not be empty list.'
                assert (
                    len(r["data"]) == 1
                ), f'Error: data {r["data"]} length should be "1"'
                assert (
                    r["data"][0]["key"] == p[0]["key"]
                ), f'Error: key {r["data"][0]["key"]} should be "{p[0]["key"]}"'
                assert r["data"][0]["code"] == int(
                    response_code
                ), f'Error: code {r["data"][0]["code"]} should be "{int(response_code)}"'
                assert (
                    r["data"][0]["error_msg"] == error_msg
                ), f'Error: error_message {r["data"][0]["error_msg"]} should be "{error_msg}"'

        # register 一把 key，但 key 不存在
        elif scenario == "key_not_found":
            # 發送 request
            with allure.step("Send HTTP request"):
                print(f"Start testing:")
                res, duration = self.test2_api.send(
                    api_key=decrypt_Test2API_key,
                    method=method,
                    url=path,
                    payload=payload,
                )
                print_result(res)

            # 驗證 response
            with allure.step("Verify response"):
                msg = "License keys activated partially."
                error_msg = "Cannot find License Key."
                p = json.loads(payload)
                r = res.json()
                assert res.status_code == int(
                    http_response
                ), f"Error: Unexpected status code {res.status_code}, expected {http_response}."
                assert (
                    r["message"] == msg
                ), f'Error: message {r["message"]} should be "{msg}"'
                assert (
                    r["pass_count"] == 0
                ), f'Error: pass_count {r["pass_count"]} should be "0"'
                assert (
                    r["fail_count"] == 1
                ), f'Error: fail_count {r["fail_count"]} should be "1"'
                assert (
                    r["data"] is not []
                ), f'Error: data {r["data"]} should not be empty list.'
                assert (
                    len(r["data"]) == 1
                ), f'Error: data {r["data"]} length should be "1"'
                assert (
                    r["data"][0]["key"] == p[0]["key"]
                ), f'Error: key {r["data"][0]["key"]} should be "{p[0]["key"]}"'
                assert r["data"][0]["code"] == int(
                    response_code
                ), f'Error: code {r["data"][0]["code"]} should be "{int(response_code)}"'
                assert (
                    r["data"][0]["error_msg"] == error_msg
                ), f'Error: error_message {r["data"][0]["error_msg"]} should be "{error_msg}"'

        # register 一把 key，但沒有帶 key 參數
        elif scenario == "missing_key":
            # 發送 request
            with allure.step("Send HTTP request"):
                print(f"Start testing:")
                res, duration = self.test2_api.send(
                    api_key=decrypt_Test2API_key,
                    method=method,
                    url=path,
                    payload=payload,
                )
                print_result(res)

            # 驗證 response
            with allure.step("Verify response"):
                msg = "License keys activated partially."
                error_msg = "Parameter [key] is missing."
                p = json.loads(payload)
                r = res.json()
                assert res.status_code == int(
                    http_response
                ), f"Error: Unexpected status code {res.status_code}, expected {http_response}."
                assert (
                    r["message"] == msg
                ), f'Error: message {r["message"]} should be "{msg}"'
                assert (
                    r["pass_count"] == 0
                ), f'Error: pass_count {r["pass_count"]} should be "0"'
                assert (
                    r["fail_count"] == 1
                ), f'Error: fail_count {r["fail_count"]} should be "1"'
                assert (
                    r["data"] is not []
                ), f'Error: data {r["data"]} should not be empty list.'
                assert (
                    len(r["data"]) == 1
                ), f'Error: data {r["data"]} length should be "1"'
                assert (
                    r["data"][0]["key"] == ""
                ), f'Error: key {r["data"][0]["key"]} should be ""'
                assert r["data"][0]["code"] == int(
                    response_code
                ), f'Error: code {r["data"][0]["code"]} should be "{int(response_code)}"'
                assert (
                    r["data"][0]["error_msg"] == error_msg
                ), f'Error: error_message {r["data"][0]["error_msg"]} should be "{error_msg}"'

        # request body 為空
        elif scenario == "missing_body":
            # 發送 request
            with allure.step("Send HTTP request"):
                res, duration = self.test2_api.send(
                    api_key=decrypt_Test2API_key,
                    method=method,
                    url=path,
                    payload=payload,
                )
                print_result(res)

            # 驗證 response
            with allure.step("Verify response"):
                msg = "Bad Request: Required request body is missing."
                r = res.json()
                assert res.status_code == int(
                    http_response
                ), f"Error: Unexpected status code {res.status_code}, expected {http_response}."
                assert (
                    r["message"] == msg
                ), f'Error: message {r["message"]} should be "{msg}"'
