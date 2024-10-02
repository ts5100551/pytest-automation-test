import os
from datetime import datetime, timedelta, timezone

import pandas as pd
import yaml

from api.base_api import BaseAPI
from common.convert import env_convert_for_mail


class TeamsMessageSender(BaseAPI):

    def __init__(
        self,
        project: str,
        env: str,
        debug: str,
        test_data_type: str,
        include_link: bool = True,
    ) -> None:
        super().__init__()
        self.project = project
        self.env = env
        self.debug = debug
        self.test_data_type = test_data_type
        self.include_link = include_link
        self.tz = timezone(timedelta(hours=+8))
        self.set_receivers()
        self.host = os.getenv("web_host")  # use env variables - web_host

    def set_receivers(self) -> None:
        config_path = os.path.join("configurations", "teams_receiver.yaml")
        with open(config_path) as f:
            d = yaml.load(f.read(), Loader=yaml.SafeLoader)

        self.receivers = d[self.project]["users"]
        self.url = (
            d[self.project]["url"] if self.debug == "0" else os.getenv("teams_noti_url")
        )  # use env variables - teams_noti_url

    def set_content(self, data: dict) -> None:
        content_data = {
            "site": env_convert_for_mail(project=self.project, env=self.env),
            "start_time": datetime.fromtimestamp(
                data["time"]["start"] / 1000.0, tz=self.tz
            ).strftime("%Y/%m/%d %H:%M:%S"),
            "end_time": datetime.fromtimestamp(
                data["time"]["stop"] / 1000.0, tz=self.tz
            ).strftime("%Y/%m/%d %H:%M:%S"),
            "cost_time": f"{data['time']['duration'] / 1000.0:.2f}",
            "count_apis": self.count_test_apis(),
            "count_total": data["statistic"]["total"],
            "count_pass": data["statistic"]["passed"],
            "count_fail": int(data["statistic"]["failed"])
            + int(data["statistic"]["broken"]),
            "count_skip": data["statistic"]["skipped"],
            "subject_result": (
                "FAIL"
                if (
                    data["statistic"]["failed"] != 0
                    or data["statistic"]["broken"] != 0
                    or data["statistic"]["unknown"] != 0
                )
                else "PASS"
            ),
        }

        self.set_receivers_payload(test_result=content_data["subject_result"])
        self.set_payload(content_data=content_data, include_link=self.include_link)

    def count_test_apis(self) -> int:
        df = pd.read_excel(f"testdata/env-{self.env}/{self.project}_TestData.xlsx")
        df = df.dropna(how="all")
        api_list = []
        for i in df["api_id"].values:
            api_list.append(i)
        count = len(set(api_list))

        return count

    def count_multi_xlsx_test_apis(self) -> int:
        directory = f"testdata/env-{self.env}/{self.project}/"
        xlsx_files = [f for f in os.listdir(directory) if f.endswith(".xlsx")]

        api_ids = set()

        for xlsx_file in xlsx_files:
            file_path = os.path.join(directory, xlsx_file)
            df = pd.read_excel(file_path).dropna(how="all")

            if "api_id" in df.columns:
                api_ids.update(df["api_id"].dropna().unique())

        return len(api_ids)

    def send(self) -> object:
        return self._send_request(
            method="POST",
            url=self.url,
            headers={"Content-Type": "application/json"},
            json=self.payload,
        )

    def set_receivers_payload(self, test_result: str) -> None:
        self.receivers_payload = {"text_mention": "", "entities": []}
        if test_result == "FAIL":
            for i, receiver in enumerate(self.receivers):
                self.receivers_payload["text_mention"] += f"<at>mention{i}</at> "

                entities_payload = {
                    "type": "mention",
                    "text": f"<at>mention{i}</at>",
                    "mentioned": {"id": receiver["id"], "name": receiver["name"]},
                }
                self.receivers_payload["entities"].append(entities_payload)

    def set_payload(self, content_data: dict, include_link: bool = True) -> None:
        self.payload = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "contentUrl": None,
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.4",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": self.receivers_payload["text_mention"],
                                "wrap": True,
                            },
                            {
                                "type": "Container",
                                "items": [
                                    {
                                        "type": "ColumnSet",
                                        "columns": [
                                            {
                                                "type": "Column",
                                                "width": 78,
                                                "items": [
                                                    {
                                                        "type": "TextBlock",
                                                        "text": self.project,
                                                        "size": "ExtraLarge",
                                                        "wrap": True,
                                                        "horizontalAlignment": "Left",
                                                        "spacing": "None",
                                                    }
                                                ],
                                                "height": "stretch",
                                                "style": "emphasis",
                                            },
                                            {
                                                "type": "Column",
                                                "width": 22,
                                                "items": [
                                                    {
                                                        "type": "TextBlock",
                                                        "text": content_data[
                                                            "subject_result"
                                                        ],
                                                        "wrap": True,
                                                        "horizontalAlignment": "Center",
                                                        "size": "ExtraLarge",
                                                        "height": "stretch",
                                                        "maxLines": 1,
                                                    }
                                                ],
                                                "spacing": "None",
                                                "style": (
                                                    "emphasis"
                                                    if content_data["subject_result"]
                                                    == "PASS"
                                                    else "attention"
                                                ),
                                                "height": "stretch",
                                            },
                                        ],
                                        "height": "stretch",
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": f"{content_data['site']} Site Test Report",
                                        "isSubtle": True,
                                        "spacing": "None",
                                        "wrap": True,
                                        "size": "Large",
                                    },
                                ],
                            },
                            {
                                "type": "Container",
                                "spacing": "Medium",
                                "items": [
                                    {
                                        "type": "ColumnSet",
                                        "columns": [
                                            {
                                                "type": "Column",
                                                "width": 70,
                                                "items": [
                                                    {
                                                        "type": "TextBlock",
                                                        "text": f"Total test APIs: {content_data['count_apis']}",
                                                        "size": "Large",
                                                        "wrap": True,
                                                    },
                                                    {
                                                        "type": "TextBlock",
                                                        "text": f"Total test Cases: {content_data['count_total']}",
                                                        "spacing": "Small",
                                                        "wrap": True,
                                                        "size": "Large",
                                                    },
                                                ],
                                                "verticalContentAlignment": "Center",
                                            },
                                            {
                                                "type": "Column",
                                                "width": 30,
                                                "items": [
                                                    {
                                                        "type": "ColumnSet",
                                                        "columns": [
                                                            {
                                                                "type": "Column",
                                                                "width": "stretch",
                                                                "items": [
                                                                    {
                                                                        "type": "TextBlock",
                                                                        "text": "PASS",
                                                                        "wrap": True,
                                                                        "color": "Good",
                                                                    }
                                                                ],
                                                            },
                                                            {
                                                                "type": "Column",
                                                                "width": "stretch",
                                                                "items": [
                                                                    {
                                                                        "type": "TextBlock",
                                                                        "text": content_data[
                                                                            "count_pass"
                                                                        ],
                                                                        "wrap": True,
                                                                    }
                                                                ],
                                                            },
                                                        ],
                                                        "spacing": "None",
                                                    },
                                                    {
                                                        "type": "ColumnSet",
                                                        "columns": [
                                                            {
                                                                "type": "Column",
                                                                "width": "stretch",
                                                                "items": [
                                                                    {
                                                                        "type": "TextBlock",
                                                                        "text": "FAIL",
                                                                        "wrap": True,
                                                                        "color": "Attention",
                                                                    }
                                                                ],
                                                            },
                                                            {
                                                                "type": "Column",
                                                                "width": "stretch",
                                                                "items": [
                                                                    {
                                                                        "type": "TextBlock",
                                                                        "text": content_data[
                                                                            "count_fail"
                                                                        ],
                                                                        "wrap": True,
                                                                    }
                                                                ],
                                                            },
                                                        ],
                                                        "spacing": "None",
                                                    },
                                                    {
                                                        "type": "ColumnSet",
                                                        "columns": [
                                                            {
                                                                "type": "Column",
                                                                "width": "stretch",
                                                                "items": [
                                                                    {
                                                                        "type": "TextBlock",
                                                                        "text": "SKIP",
                                                                        "wrap": True,
                                                                        "color": "Warning",
                                                                    }
                                                                ],
                                                            },
                                                            {
                                                                "type": "Column",
                                                                "width": "stretch",
                                                                "items": [
                                                                    {
                                                                        "type": "TextBlock",
                                                                        "text": content_data[
                                                                            "count_skip"
                                                                        ],
                                                                        "wrap": True,
                                                                    }
                                                                ],
                                                            },
                                                        ],
                                                        "spacing": "None",
                                                    },
                                                ],
                                                "separator": True,
                                                "spacing": "Large",
                                            },
                                        ],
                                    }
                                ],
                                "separator": True,
                            },
                            {
                                "type": "Container",
                                "items": [
                                    {
                                        "type": "ColumnSet",
                                        "columns": [
                                            {
                                                "type": "Column",
                                                "width": "auto",
                                                "items": [
                                                    {
                                                        "type": "TextBlock",
                                                        "text": "Cost Time:",
                                                        "wrap": True,
                                                        "color": "Accent",
                                                    }
                                                ],
                                            },
                                            {
                                                "type": "Column",
                                                "width": "auto",
                                                "items": [
                                                    {
                                                        "type": "TextBlock",
                                                        "text": f" {content_data['cost_time']} sec.",
                                                        "wrap": True,
                                                    }
                                                ],
                                            },
                                        ],
                                    }
                                ],
                                "spacing": "Medium",
                                "separator": True,
                            },
                            {
                                "type": "ColumnSet",
                                "columns": [
                                    {
                                        "type": "Column",
                                        "width": "stretch",
                                        "items": [
                                            {
                                                "type": "TextBlock",
                                                "text": f"{content_data['start_time']} ~ {content_data['end_time']}",
                                                "wrap": True,
                                                "spacing": "None",
                                            }
                                        ],
                                    }
                                ],
                                "spacing": "None",
                            },
                            {
                                "type": "Container",
                                "items": [
                                    {
                                        "type": "ColumnSet",
                                        "columns": [
                                            {
                                                "type": "Column",
                                                "width": "auto",
                                                "items": [
                                                    {
                                                        "type": "TextBlock",
                                                        "text": "Testing Report Link:",
                                                        "wrap": True,
                                                        "color": "Accent",
                                                    }
                                                ],
                                            },
                                            {
                                                "type": "Column",
                                                "width": "stretch",
                                                "items": [
                                                    {
                                                        "type": "TextBlock",
                                                        "text": f"{self.project} {content_data['site']} Report",
                                                        "wrap": True,
                                                        "isSubtle": True,
                                                    }
                                                ],
                                                "selectAction": {
                                                    "type": "Action.OpenUrl",
                                                    "url": f"http://{self.host}/report/{self.project}/{self.env}/index.html",  # use env variables - host
                                                },
                                            },
                                        ],
                                    }
                                ],
                                "separator": True,
                            },
                            {
                                "type": "Container",
                                "items": [
                                    {
                                        "type": "ColumnSet",
                                        "columns": [
                                            {
                                                "type": "Column",
                                                "width": "auto",
                                                "items": [
                                                    {
                                                        "type": "TextBlock",
                                                        "text": "Toolset Report Link:",
                                                        "wrap": True,
                                                        "color": "Accent",
                                                    }
                                                ],
                                            },
                                            {
                                                "type": "Column",
                                                "width": "auto",
                                                "items": [
                                                    {
                                                        "type": "TextBlock",
                                                        "text": "Statistical Report",
                                                        "wrap": True,
                                                        "isSubtle": True,
                                                    }
                                                ],
                                                "selectAction": {
                                                    "type": "Action.OpenUrl",
                                                    "url": f"http://{self.host}/index.html",  # use env variables - host
                                                },
                                            },
                                        ],
                                    }
                                ],
                                "spacing": "None",
                            },
                        ],
                        "verticalContentAlignment": "Top",
                        "msteams": {"entities": self.receivers_payload["entities"]},
                    },
                }
            ],
        }
