import os
import subprocess

import requests

# 設定的容量大小 MB
MAX_CAPACITY_MB = 500
TEAMS_URL = os.getenv("teams_noti_url")


def get_folder_size(folder):
    """
    計算資料夾的大小並轉換為MB
    :param folder: 資料夾的路徑
    :return: 資料夾大小(MB)
    """
    result = subprocess.run(["du", "-s", folder], stdout=subprocess.PIPE)
    size_str = result.stdout.decode("utf-8").split()[0]
    total_size = int(size_str) / 1024  # 轉換成MB
    return total_size


def notify(folders):
    """
    發送通知到 Microsoft Teams, 如果有資料夾超過設定容量, 則列出其詳細信息
    :param folders: 超過設定容量的資料夾列表
    """
    card_body = [
        {
            "type": "Container",
            "items": [
                {
                    "type": "TextBlock",
                    "text": "Toolset report folder capacity",
                    "wrap": True,
                    "style": "heading",
                    "size": "Large",
                    "weight": "Bolder",
                    "color": "Attention",
                    "isSubtle": True,
                    "spacing": "ExtraLarge",
                }
            ],
        }
    ]

    if not folders:
        # 如果沒有資料夾超過設定容量，顯示相應信息
        card_body.append(
            {
                "type": "Container",
                "items": [
                    {
                        "type": "TextBlock",
                        "text": f"All folder capacities are lower than {MAX_CAPACITY_MB} MB.",
                        "wrap": True,
                        "size": "small",
                        "isSubtle": True,
                    }
                ],
            }
        )
    else:
        # 如果有資料夾超過設定容量，顯示相應信息和詳細列表
        card_body.append(
            {
                "type": "Container",
                "items": [
                    {
                        "type": "TextBlock",
                        "text": f"The capacity of the following folders exceeds the set value of {MAX_CAPACITY_MB} MB.",
                        "wrap": True,
                        "size": "small",
                        "isSubtle": True,
                    }
                ],
            }
        )

        # 建立資料夾詳細信息的表格
        table_rows = [
            {
                "type": "TableRow",
                "cells": [
                    {
                        "type": "TableCell",
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": "Project",
                                "wrap": True,
                                "horizontalAlignment": "Center",
                                "color": "Default",
                                "style": "heading",
                                "size": "medium",
                            }
                        ],
                    },
                    {
                        "type": "TableCell",
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": "Environment",
                                "wrap": True,
                                "horizontalAlignment": "Center",
                                "color": "Default",
                                "style": "heading",
                                "size": "medium",
                            }
                        ],
                    },
                    {
                        "type": "TableCell",
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": "Capacity (MB)",
                                "horizontalAlignment": "Center",
                                "wrap": True,
                                "color": "Default",
                                "style": "heading",
                                "size": "medium",
                            }
                        ],
                    },
                ],
            }
        ]

        # 添加每個超過設定容量的資料夾信息到表格中
        for project, env, capacity in folders:
            table_rows.append(
                {
                    "type": "TableRow",
                    "cells": [
                        {
                            "type": "TableCell",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": project,
                                    "wrap": True,
                                    "horizontalAlignment": "Center",
                                    "color": "Default",
                                    "style": "heading",
                                    "size": "medium",
                                }
                            ],
                        },
                        {
                            "type": "TableCell",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": env,
                                    "wrap": True,
                                    "horizontalAlignment": "Center",
                                    "color": "Default",
                                    "style": "heading",
                                    "size": "medium",
                                }
                            ],
                        },
                        {
                            "type": "TableCell",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": str(capacity),
                                    "horizontalAlignment": "Center",
                                    "wrap": True,
                                    "color": "Default",
                                    "style": "heading",
                                    "size": "medium",
                                }
                            ],
                        },
                    ],
                }
            )

        # 將表格添加到卡片內容中
        card_body.append(
            {
                "type": "Table",
                "columns": [{"width": 1}, {"width": 1}, {"width": 1}],
                "rows": table_rows,
            }
        )

    # 構建 Adaptive Card
    adaptive_card = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": None,
                "content": {
                    "type": "AdaptiveCard",
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "version": "1.5",
                    "fallbackText": "This card requires Adaptive Cards v1.5 support to be rendered properly.",
                    "body": card_body,
                    "verticalContentAlignment": "Top",
                    "minHeight": "0px",
                },
            }
        ],
    }

    # 發送 POST 請求到 Microsoft Teams Webhook
    response = requests.post(
        url=TEAMS_URL, json=adaptive_card, headers={"Content-Type": "application/json"}
    )
    response.raise_for_status()  # 確保請求成功，否則會引發錯誤


def main():
    """
    主函數, 執行資料夾大小檢查並通知超過容量限制的資料夾
    """
    base_path = "./report"
    exceeding_folders = []

    # 列出 /report 資料夾底下所有專案的資料夾名稱
    projects = [
        d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))
    ]

    for project in projects:
        project_path = os.path.join(base_path, project)

        # 找到專案資料夾內的第二層環境資料夾
        env_folders = [
            d
            for d in os.listdir(project_path)
            if os.path.isdir(os.path.join(project_path, d))
        ]

        for env in env_folders:
            env_path = os.path.join(project_path, env)

            # 檢查資料夾容量大小
            folder_size = round(get_folder_size(env_path), 2)
            if folder_size > MAX_CAPACITY_MB:
                exceeding_folders.append((project, env, folder_size))

    # 執行 notify 的 function
    notify(exceeding_folders)


if __name__ == "__main__":
    main()
