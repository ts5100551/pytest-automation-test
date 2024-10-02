import json
import os
from datetime import datetime, timedelta, timezone

import cryptocode
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def decrypt_key(key: str, pwd: str) -> str:
    return cryptocode.decrypt(key, pwd)


def print_payload(payload: dict, title: str = "") -> None:
    print(title) if title != "" else None
    print(json.dumps(payload, indent=2))
    print("")


def print_result(res: object, title: str = "") -> None:
    print(title) if title != "" else None
    print(f"HTTP response status code: {res.status_code}")
    if res.status_code == 200:
        try:
            print(
                f"HTTP response data:\n{json.dumps(json.loads(res.text), indent=2, ensure_ascii=False)}"
            )
        except:
            print(f"HTTP response data:\n{res.text}")
    else:
        print(f"HTTP response data:\n{res.text}")
    print("")


def get_datetime(type: str) -> str:
    tz = timezone(timedelta(hours=+8))
    if type == "datetime_s":
        time = str(
            datetime.now(tz).strftime("%Y%m%d%H%M%S")
        )  # 年月日時分秒 ex. 20220520091559
    elif type == "datetime_ns":
        time = str(
            datetime.now(tz).strftime("%Y%m%d%H%M")
        )  # 年月日時分 ex. 202205200915
    elif type == "date_y":
        time = str(datetime.now(tz).strftime("%Y%m%d"))  # 年月日 ex. 20220520
    elif type == "date_ny":
        time = str(datetime.now(tz).strftime("%m%d"))  # 月日 ex. 0520
    else:
        time = ""
    return time


def get_test_result(project: str, env: str) -> dict:
    with open(f"report/{project}/{env}/html/widgets/summary.json") as f:
        data = json.load(f)

    return data


def open_browser(headless: bool = True) -> object:
    # disabled geckodriver.log
    firefox_service = Service(log_path=os.path.devnull)

    # False: 介面模式, True: 無介面模式
    if headless == True:
        firefox_options = Options()
        firefox_options.add_argument("--window-size=1920,1080")
        firefox_options.add_argument("--headless")
        driver = webdriver.Firefox(service=firefox_service, options=firefox_options)
    else:
        driver = webdriver.Firefox(service=firefox_service)

    return driver


def browser_login_account(driver: object, url: str, username: str, password: str):
    # MZC portal login
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "user_email"))
    )
    driver.find_element(By.ID, "user_email").send_keys(username)
    driver.find_element(By.ID, "user_password").send_keys(password)
    driver.find_element(By.ID, "user_password").send_keys(Keys.ENTER)


def check_has_fail_case(data: dict) -> bool:
    return (
        True
        if (
            data["statistic"]["failed"] != 0
            or data["statistic"]["broken"] != 0
            or data["statistic"]["unknown"] != 0
        )
        else False
    )


def get_current_datetime_iso8601() -> str:
    now_utc = datetime.now(timezone.utc)
    delta = timedelta(hours=8)
    now_utc_plus_8 = now_utc + delta
    return now_utc_plus_8.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
