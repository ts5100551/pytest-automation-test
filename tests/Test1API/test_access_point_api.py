import allure
import pytest

from api.test1_api import Test1API
from common.common import print_result
from common.load_excel import load_data, load_ids


class TestAccessPoint(object):

    test1_api = Test1API()

    @pytest.mark.test
    @pytest.mark.prod
    @pytest.mark.parametrize(
        "api_id, case_id, path, description, run, env, key, method, http_response, user_id, url, payload",
        load_data(site="test1", api_id="test1-ap-01"),
        ids=load_ids(site="test1", api_id="test1-ap-01"),
    )
    def test_ap_01(
        self,
        is_run,
        decrypt_Test1API_key,
        api_id,
        case_id,
        path,
        description,
        run,
        env,
        key,
        method,
        http_response,
        user_id,
        url,
        payload,
    ):

        # Allure report 參數設定
        allure.dynamic.story("API Category: AccessPoint")
        allure_title = f"{api_id}_{key}_{http_response}"
        allure.dynamic.title(
            allure_title.replace("-", "_")
        )  # 用底線可讓 case 在 report 中的 title 不被換行，比較好看
        allure.dynamic.description(description)

        # 透過 test data excel 的 is_run 欄位值決定是否要執行該 case 的測試
        if not is_run(is_run=run):
            pytest.skip()

        # 進行 API request 並輸出結果
        with allure.step("Send HTTP request"):
            d_key = decrypt_Test1API_key
            res, duration = self.test1_api.send(
                user_id=user_id,
                key=key,
                api_key=d_key,
                method=method,
                url=url,
                payload=payload,
            )
            print_result(res)

        # 驗證階段
        with allure.step("Verify response status code"):
            assert str(res.status_code) == http_response

    @pytest.mark.test
    @pytest.mark.prod
    @pytest.mark.parametrize(
        "api_id, case_id, path, description, run, env, key, method, http_response, user_id, url, payload",
        load_data(site="test1", api_id="test1-ap-02"),
        ids=load_ids(site="test1", api_id="test1-ap-02"),
    )
    def test_ap_02(
        self,
        is_run,
        decrypt_Teset1API_key,
        api_id,
        case_id,
        path,
        description,
        run,
        env,
        key,
        method,
        http_response,
        user_id,
        url,
        payload,
    ):

        # Allure report 參數設定
        allure.dynamic.story("API Category: AccessPoint")
        allure_title = f"{api_id}_{key}_{http_response}"
        allure.dynamic.title(
            allure_title.replace("-", "_")
        )  # 用底線可讓 case 在 report 中的 title 不被換行，比較好看
        allure.dynamic.description(description)

        # 透過 test data excel 的 is_run 欄位值決定是否要執行該 case 的測試
        if not is_run(is_run=run):
            pytest.skip()

        # 進行 API request 並輸出結果
        with allure.step("Send HTTP request"):
            d_key = decrypt_Teset1API_key[key]
            res, duration = self.test1_api.send(
                user_id=user_id,
                key=key,
                api_key=d_key,
                method=method,
                url=url,
                payload=payload,
            )
            print_result(res)

        # 驗證階段
        with allure.step("Verify response status code"):
            assert str(res.status_code) == http_response

    @pytest.mark.test
    @pytest.mark.prod
    @pytest.mark.parametrize(
        "api_id, case_id, path, description, run, env, key, method, http_response, user_id, url, payload",
        load_data(site="test1", api_id="test1-ap-03"),
        ids=load_ids(site="test1", api_id="test1-ap-03"),
    )
    def test_ap_03(
        self,
        is_run,
        decrypt_Teset1API_key,
        api_id,
        case_id,
        path,
        description,
        run,
        env,
        key,
        method,
        http_response,
        user_id,
        url,
        payload,
    ):

        # Allure report 參數設定
        if key == "ec":
            allure.dynamic.feature("EC Key")
        elif key == "customer":
            allure.dynamic.feature("Customer Key")
        allure.dynamic.story("API Category: AccessPoint")
        allure_title = f"{api_id}_{key}_{http_response}"
        allure.dynamic.title(
            allure_title.replace("-", "_")
        )  # 用底線可讓 case 在 report 中的 title 不被換行，比較好看
        allure.dynamic.description(description)

        # 透過 test data excel 的 is_run 欄位值決定是否要執行該 case 的測試
        if not is_run(is_run=run):
            pytest.skip()

        # 進行 API request 並輸出結果
        with allure.step("Send HTTP request"):
            d_key = decrypt_Teset1API_key[key]
            res, duration = self.test1_api.send(
                user_id=user_id,
                key=key,
                api_key=d_key,
                method=method,
                url=url,
                payload=payload,
            )
            print_result(res)

        # 驗證階段
        with allure.step("Verify response status code"):
            assert str(res.status_code) == http_response
