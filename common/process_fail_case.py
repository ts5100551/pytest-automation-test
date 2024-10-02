import json
import os

import jwt
import requests


def perform(case_data: list, project: str, env: str) -> None:

    # 資料並不是在 json 的第一層，因此用遞迴方法抓到最內層的目標資料
    if "children" in case_data:
        for children in case_data["children"]:
            perform(case_data=children, project=project, env=env)

    else:
        uid = case_data["uid"]
        name = case_data["name"]
        start_time = case_data["time"]["start"]

        attachments = []
        # 取該測試案例的 json file 檔名
        test_case_file_name = f"{start_time}_{uid}_testfile.json"
        attachments.append(test_case_file_name)

        # 透過 uid 找到該測試案例的 json 檔案
        with open(
            f'report/{project}/{env}/html/data/test-cases/{case_data["uid"]}.json'
        ) as f:
            test_case_file = json.load(f)

        # 取該測試案例的 description 資料
        description = (
            test_case_file["description"] if "description" in test_case_file else ""
        )

        # 取該測試案例的 log file 檔名
        if test_case_file["testStage"]["attachments"]:
            log_file_name = (
                str(start_time)
                + "_"
                + test_case_file["testStage"]["attachments"][0]["source"].split(".")[0]
                + "_logfile.txt"
            )
            attachments.append(log_file_name)

        if test_case_file["parameters"]:
            api_path = next(
                (
                    parameter["value"]
                    for parameter in test_case_file["parameters"]
                    if parameter["name"] == "path"
                ),
                "",
            )
        else:
            api_path = ""

        # 準備打 API 的 payload
        case_payload = {
            "environment": env,
            "project": project,
            "timestamp": int(start_time),
            "caseUId": uid,
            "caseName": name,
            "caseDescription": description,
            "attachments": attachments,
            "apiPath": api_path,
        }

        # 打 API 將資料寫入 DynamoDB
        try:
            res = insert_case_data_to_dynamodb(payload=case_payload)
        except Exception as e:
            raise Exception(f"Insert Failure Case Data to DynamoDB Error: {e}")
        else:
            if res.status_code != 200:
                raise Exception(
                    f"Insert Failure Case Data to DynamoDB Error, Response: {res.status_code}"
                )

        file_list = []
        # 準備 test case json file 的內容，使用 jwt 加密文字後再傳輸
        file_list.append(
            {
                "filename": test_case_file_name,
                "content": jwt.encode(
                    test_case_file, os.getenv("pwd"), algorithm="HS256"
                ),
            }
        )
        # 準備 log file 的內容
        if test_case_file["testStage"]["attachments"]:
            with open(
                f'report/{project}/{env}/html/data/attachments/{test_case_file["testStage"]["attachments"][0]["source"]}',
                "r",
            ) as data:

                file_list.append(
                    {
                        "filename": log_file_name,
                        "content": jwt.encode(
                            {"content": data.read()},
                            os.getenv("pwd"),
                            algorithm="HS256",
                        ),
                    }
                )

        file_payload = {"environment": env, "project": project, "files": file_list}

        # 打 API 將資料寫入 S3
        try:
            res = upload_case_file_to_s3(payload=file_payload)
        except Exception as e:
            raise Exception(f"Upload Test Data to S3 Error: {e}")
        else:
            if res.status_code != 200:
                raise Exception(
                    f"Upload Test Data to S3 Error, Response: {res.status_code}"
                )


def insert_case_data_to_dynamodb(payload: dict) -> dict:
    url = os.getenv("insert_dynamodb_api")  # use env variables - url
    headers = {"Content-Type": "application/json"}
    response = requests.request("POST", url, json=payload, headers=headers)
    return response


def upload_case_file_to_s3(payload: dict) -> dict:
    url = os.getenv("upload_s3_api")  # use env variables - url
    headers = {"Content-Type": "application/json"}
    response = requests.request("POST", url, json=payload, headers=headers)
    return response


def process_fail_data(project: str, env: str) -> None:
    # 只要有 fail 就會記錄在 categories.json 檔案內
    with open(f"report/{project}/{env}/html/data/categories.json") as f:
        categories_data = json.load(f)

    # 將每一個 fail 的 case 讀取執行 perform 方法將資料打 Lambda API 寫入 DB, S3
    for cases in categories_data["children"]:
        perform(case_data=cases, project=project, env=env)
