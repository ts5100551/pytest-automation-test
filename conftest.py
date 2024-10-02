import json
import os
import shutil
import time
from time import sleep

import allure
import pytest
import yaml
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from api.test1_api import Test1API
from api.test2_api import Test2API
from common.common import browser_login_account, decrypt_key, get_datetime, open_browser


# 抓取 cmd 指令的 --env 參數作為後續測試的環境指定，預設是 test
def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        dest="environment",
        default="test",
        help="environment: test or prod",
    )


# 此 func 是類似執行測試前的 init 動作
# 根據 --env 的值將各環境的 config 檔案複製到 ./configurations 中，後續程式都只要讀取該檔案即可切換環境
def pytest_configure(config):
    env = config.getoption("--env").lower()

    try:
        shutil.copyfile(
            f"./configurations/{env}/config.yaml", "./configurations/config.yaml"
        )
    except Exception as e:
        print(f"Invalid Environment: {env}, Error Message: {e}")


# 判斷該 test case 是否要進行測試，由 excel test data 中的 is_run 值控制
@pytest.fixture(scope="function")
def is_run():

    def check(is_run: int):
        if not (int(is_run) == 1):
            pytest.skip(f"Skip by test data setting, is_run: {is_run}")
            return False
        else:
            return True

    return check


# 在測試開始時做 Test1 API X-API-Key 的解密，因設置成 session，因此整個測試只會做一次，可以共享到每個 case
# 可以省去每個 case 都要去做解密的動作，減少運算資源
@pytest.fixture(scope="session")
def decrypt_Test1API_key():
    test1_api = Test1API()
    config_path = os.path.join("configurations", "config.yaml")
    with open(config_path) as f:
        d = yaml.load(f.read(), Loader=yaml.SafeLoader)

    key = d["Test1API"]["key"], pwd = test1_api.pwd

    return key


@pytest.fixture(scope="session")
def decrypt_Test2API_key() -> str:
    test2_api = Test2API()
    return test2_api.get_api_key()


@pytest.fixture(scope="function")
def login_mzc_beta_hq_account():
    # Parameters
    url = os.getenv("test_login_url")
    username = os.getenv("user_acc")
    password = os.getenv("user_pwd")

    # Open browser
    driver = open_browser(headless=True)
    driver.maximize_window()

    try:
        # Portal login
        browser_login_account(
            driver=driver, url=url, username=username, password=password
        )

        # Wait until page loaded and switch role
        element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "staff_id"))
        )
        driver.find_element(By.ID, "staff_id").click()
        sel = driver.find_element(By.ID, "staff_id")
        Select(sel).select_by_visible_text("Headquarter")
        sleep(2)
        element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "/html/body/div[1]/div[3]/ul/li[8]/ul/li[1]/a")
            )
        )
    except:
        logger.error(f"Selenium error in Sign In page.")
        driver.quit()
        pytest.fail("Test fail because Selenium error")

    # 將目前狀態回傳給測試案例
    yield driver

    # 測試完畢關閉瀏覽器
    driver.quit()


@pytest.fixture(scope="function")
def login_mzc_beta_user_account():
    # Parameters
    url = os.getenv("test_login_url")
    username = os.getenv("hq_account")
    password = os.getenv("hq_pwd")

    # Open browser
    driver = open_browser(headless=True)
    driver.maximize_window()

    try:
        # MZC portal login
        browser_login_account(
            driver=driver, url=url, username=username, password=password
        )

        # Check My Devices tag is loaded
        element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "/html/body/div[1]/div[3]/ul/div[1]/li/ul/li[1]/a")
            )
        )
        sleep(2)
    except:
        logger.error(f"Selenium error in Sign In page.")
        driver.quit()
        pytest.fail("Test fail because Selenium error")

    # 將目前狀態回傳給測試案例
    yield driver

    # 測試完畢關閉瀏覽器
    driver.quit()
